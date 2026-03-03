import ms_classes as cls
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import pygame.mixer
from random import choice
import time
import os
import stat
import sys


def resource_path(relative_path):
    try:
        # pyinstaller creating the temp dir and keeping the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # launch from the program folder (onedir mode)
        base_path = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

def main():
    exit, mute, start = False, False, None
    target_cell, prev_cell = None, None
    levels = {"10 dicks" : 10, "15 dicks" : 15, "20 dicks" : 20}
    level = tuple(levels.items())[0]
    appdata_roaming = os.getenv('APPDATA')

    game_data_folder = os.path.join(appdata_roaming, "Men's♂wee-weeper")
    if not os.path.exists(game_data_folder):
        os.makedirs(game_data_folder)  # will create a dir, if it doesn't exist

    save_file = os.path.join(game_data_folder, "records.txt")

    try:
        recordsmen = {}
        with open(save_file, 'r', encoding="utf-8") as records:
            for lvl in levels:
                recordsmen[lvl] = tuple(records.readline().rstrip().split(", "))
    except FileNotFoundError:
        pass

    while not exit:
        def show_open(mode):
            # получаем таблицы соответствия "(координаты клетки) -> номер объекта canvas" для слоя изображений и слоя текста
            img_table = get_table(101)
            txt_table = get_table(201)

            for i in range(field.n):
                for j in range(field.n):
                    cell = field.field[i][j]
                    if mode == "show":
                        if not cell.is_open:
                            canvas.itemconfigure(img_table[(i, j)], image=dropplets_img if cell.is_tagged else transp_sq)
                        else:
                            if cell.is_mine:
                                canvas.itemconfigure(img_table[(i, j)], image=eggplant_img)
                            elif cell.is_tagged:
                                canvas.itemconfigure(img_table[(i, j)], image=transp_sq)
                                field.tags -= 1
                            else:
                                canvas.itemconfigure(txt_table[(i, j)], text=f"{cell.number}" if cell.number != 0 else "")
                    elif mode == "open":
                        if cell.is_tagged:
                            canvas.itemconfigure(img_table[(i, j)], image=transp_sq if not cell.is_mine else eggplant_img)
                        else:
                            if not cell.is_mine:
                                canvas.itemconfigure(txt_table[(i, j)], text=f"{cell.number}" if cell.number != 0 else "")
                            else:
                                canvas.itemconfigure(img_table[(i, j)], image=eggplant_img)
                        fill_opened_cells(all=True)
                print()

        def fill_opened_cells(all):
            # получаем таблицу соответствия для слоя клеток (чтобы менять их заливку)
            cells_table = get_table(1)

            for i in range(field.n):
                for j in range(field.n):
                    cell = field.field[i][j]
                    if not all:
                        if cell.is_open:
                            # отмечаем красной заливкой клетку с миной, на которой произошел подрыв
                            canvas.itemconfigure(cells_table[(i, j)], fill="#fa0202" if cell.is_mine else '#56b6c2')
                    if all:
                        if cell.is_tagged:
                            # визуализируем заливкой правильность установленных флагов
                            canvas.itemconfigure(cells_table[(i, j)], fill="#76f1bc" if cell.is_mine else "#ffacb6")
                        else:
                            # клетка с миной, на которой игрок подорвался, осталась красной
                            if canvas.itemcget(cells_table[(i, j)], option="fill") != "#fa0202":
                                canvas.itemconfigure(cells_table[(i, j)], fill='#56b6c2')

        def left_click(event):
            nonlocal field

            # start the session timer
            start_time()

            for key, value in images.items():
                if (key[0] - 25 < event.x < key[0] + 25 and key[1] - 25 < event.y < key[1] + 25):
                    i, j = img_table_rvrs[value]
                    cell = field.field[i][j]
                    if cell and not cell.is_tagged:
                        # safe first move implementation
                        if field.closed == field.n ** 2 and cell.is_mine:
                            while 1:
                                field = get_init_field(level)
                                if not field.field[i][j].is_mine:
                                    cell = field.field[i][j]
                                    break
                        closed_before = field.closed
                        field.open_cell(i, j)
                        fill_opened_cells(all=False)
                        if cell.is_mine:
                            lose_win("lose")
                        else:
                            if field.closed == field.total_mines:
                                lose_win("win")
                            else:
                                if closed_before - field.closed > 1:
                                    play_sound("nice", pool=False)
                                else:
                                    play_sound("move")
                                show_open("show")
                                status_bar_left.config(text=f"Nice move! Tags set: {field.tags}. Cells left to open: {field.closed - field.total_mines}.")

        def right_click(event):
            # start the session timer
            start_time()

            for key, value in images.items():
                if (key[0] - 25 <= event.x <= key[0] + 25 and key[1] - 25 <= event.y <= key[1] + 25):
                    i, j = img_table_rvrs[value]
                    cell = field.field[i][j]
                    if not cell.is_open:
                        cell.is_tagged = not cell.is_tagged
                        field.tags = field.tags + 1 if cell.is_tagged else field.tags - 1
                        play_sound("tag")
                        show_open("show")
                        status_bar_left.config(text=f"The tag is {"" if cell.is_tagged else "un"}set! Tags set: {field.tags}. Cells left to open: {field.closed - field.total_mines}.")

        def get_secs_from_hhmmss(hhmmss : str):
            parse_time = [int(x) for x in hhmmss.split(":")]
            return parse_time[0] * 3600 + parse_time[1] * 60 + parse_time[2]

        def lose_win(message):
            nonlocal recordsmen, exit, level, start

            play_sound(message)
            show_open("open")

            stop_hhmmss = get_time_in_hhmmss()
            status_bar_left.config(text=f"Game over. Time: {stop_hhmmss}")
            stop_time()
            session_time_right.config(text="")

            if recordsmen and message == "win" and get_secs_from_hhmmss(stop_hhmmss) < get_secs_from_hhmmss(recordsmen[level[0]][1]):
                name = "wee"
                while name is not None and not 4 <= len(name) <= 30:
                    name = simpledialog.askstring("All hail the new boss!", " " * 5 + "Input your name! (from 4 to 30 chars)" + " " * 5)
                if name is not None:
                    recordsmen[level[0]] = (name, stop_hhmmss)
                    try:
                        os.chmod(save_file, stat.S_IWRITE)
                        with open(save_file, 'r+', encoding="utf-8") as records:
                            records.truncate()
                            values_as_strings = [", ".join(x) + "\n" for x in recordsmen.values()]
                            st_to_write = "".join(values_as_strings).rstrip("\n")
                            records.writelines(st_to_write)
                        os.chmod(save_file, 0o444)
                    except FileNotFoundError as error:
                        messagebox.showerror("Error", error)

            result = messagebox.askyesno("Game over", f"You {message}! Wish you try once more?")
            if not result:
                exit = True  # Exit the loop if "No" is pressed
            start = None
            root.destroy()
                
        def push_exit():
            nonlocal exit

            result = messagebox.askyesno("Exit", "Are you sure you want to quit?")
            if result:
                root.destroy()
                exit = True  # Exit the loop if "Yes" is pressed

        def mute_func():
            nonlocal mute
            mute = not mute

        def play_sound(mode, pool=True):
            if not mute:
                prefix, postfix = "sounds/", ".mp3"
                try:
                    if pool:
                        match mode:
                            case "lose":
                                fix = choice(["aaah", "victim", "augh", "fuck_you", "leather_man", "lube_it_up", "suction"])
                            case "move":
                                fix = choice(["thats_amazing", "yes", "spank_1", "spank_2", "spank_3", "woo"])
                            case "start":
                                fix = choice(["lash", "make_me_cum", "that_turns_me_on", "stick_finger"])
                            case "tag":
                                fix = choice(["ass_we_can", "fucking_deep", "mmmm", "eargasm_1", "eargasm_2"])
                            case "win":
                                fix = choice(["celebrate", "dungeon_master", "wee_wee"])
                    else:
                        fix = mode
                    pygame.mixer.music.load(resource_path(prefix + fix + postfix))
                    pygame.mixer.music.play()
                except FileNotFoundError:
                    messagebox.showerror("Error", "Audio files were not found in the directory. Mute mode is enabled")
                    mute_func()     

        def get_init_field(level):
            new_field = cls.GameField(10, level[1])
            new_field.init_field()
            return new_field
        
        def set_level(value : str):
            nonlocal level
            level = (value, levels[value])
            root.destroy()

        def show_records():
            nonlocal levels

            table = tk.Toplevel(root)

            style = ttk.Style()
            style.theme_use('clam')
            style.configure("Custom.Treeview", font=('Segoe UI', 11))
            style.configure("Custom.Treeview.Heading", foreground="white", background='#56b6c2', font=('Segoe UI', 12, "bold"), relief='None')
            style.map("Custom.Treeview.Heading", background=[('active', '#56b6c2')])

            table.title("Hall of fame")
            w = root.winfo_screenwidth()
            h = root.winfo_screenheight()
            w = w//2 # middle of the screen
            h = h//2 
            table.geometry('350x120+{}+{}'.format(w - 180, h - 40))

            table.resizable(False, False)

            # define columns
            columns = ("level", "name", "time")

            # create the Treeview widget
            # show="headings" hides the default first column used for the tree hierarchy
            tree = ttk.Treeview(table, columns=columns, show='headings', style="Custom.Treeview")

            # configure column headings and widths
            tree.heading("level", text="Level", anchor=tk.CENTER)
            tree.heading("name", text="Name", anchor=tk.CENTER)
            tree.heading("time", text="Time", anchor=tk.CENTER)
            tree.column("level", width=35, anchor=tk.CENTER)
            tree.column("name", width=145, anchor=tk.CENTER)
            tree.column("time", width=50, anchor=tk.CENTER)

            level_names = tuple(levels)
            recordsmen_values = [list(x) for x in list(recordsmen.values())]
            recordsmen_lst = [[level_names[i]] + recordsmen_values[i] for i in range(3)]

            # insert data into the Treeview
            for item in recordsmen_lst:
            # "" means no parent (top level item), "end" means insert at the end of the list
                tree.insert("", tk.END, values=item)

            play_sound("do_you_like", pool=False)

            # pack the widgets
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        def start_time():
            nonlocal start
            # if all cells are closed, start the session timer
            if field.closed == field.n ** 2 and not start:
                start = time.time()
                update_time()

        def update_time():
            global session_stop
            session_time_right.config(text=f"{get_time_in_hhmmss()}")
            session_stop = root.after(1000, update_time)

        def stop_time():
            global session_stop
            root.after_cancel(session_stop)
            session_stop = None
                
        def get_table(seed : int, reverse=False):
            cnt = seed
            table = {}
            for j in range(10):
                for i in range(10):
                    if not reverse:
                        table[(i, j)] = cnt
                    else:
                        table[cnt] = (i, j)
                    cnt += 1
            return table
        
        def get_time_in_hhmmss():
            return time.strftime("%H:%M:%S", time.gmtime(time.time() - start))
        
        # event handler - "cursor hovers over a closed cell"
        def on_motion(event):
            #=^.^=
            nonlocal target_cell, prev_cell
            cell_table = get_table(1, True)
            for key in cells:
                if key[0][0] < event.x < key[0][1] and key[1][0] < event.y < key[1][1]:
                    i, j = cell_table[cells[key]]
                    cell = field.field[i][j]
                    if cell:
                        # get all objects under the cursor (in stack order, bottom to top)
                        objects_under = canvas.find_overlapping(event.x, event.y, event.x, event.y)

                        # looking for the first object with the tag "cell"
                        for obj in objects_under:
                            tags = canvas.gettags(obj)
                            if "cell" in tags:
                                target_cell = obj
                                break

                        # if the target object is found and it has changed
                        if target_cell and target_cell != prev_cell:
                            # remove the fill from the previous one
                            if prev_cell and canvas.itemcget(prev_cell, option="fill") != '#56b6c2':
                                canvas.itemconfigure(prev_cell, fill='light blue')
                            # filling the next one, moving on to the next one
                            if canvas.itemcget(target_cell, option="fill") != '#56b6c2':
                                canvas.itemconfigure(target_cell, fill='light grey')
                                prev_cell = target_cell
                    else:
                        on_leaving(event)
        # if the cursor is out of the field, return the fill to its original state        
        def on_leaving(event):
            nonlocal target_cell, prev_cell
            for value in cells.values():
                if canvas.itemcget(value, option="fill") == "light grey":
                    canvas.itemconfigure(value, fill='light blue')
                    prev_cell = target_cell = None
        
        # getting the reverse lookup table for the image layer - to determine the cell that was clicked
        img_table_rvrs = get_table(101, True)

        # mixer initialization (if mute == False)
        if not mute:
            pygame.mixer.init()
        
        # greeting, sound accompaniment
        play_sound("start")

        # field creating + initialization, default level = "Easy / 10 mines"
        field = get_init_field(level)

        # main window, creating + configuration
        root = tk.Tk()
        root.title("Men's♂wee-weeper")
        root.geometry("510x560")
        try:
            root.iconbitmap(default=resource_path("images/darkholme.ico"))
        except FileNotFoundError:
            root.iconbitmap()

        # canvas, creating + configuration
        canvas = tk.Canvas(bg="white", width=501, height=501)
        canvas.pack(anchor=tk.CENTER)
        canvas.bind("<Button-1>", left_click)
        canvas.bind("<Button-3>", right_click)
        canvas.bind("<Motion>", on_motion)
        canvas.bind("<Leave>", on_leaving)

        # creating the layer of cells (1st)
        cells = {}
        for i in range(2, 502, 50):
            for j in range(2, 502, 50):
                cell = canvas.create_rectangle(i, j, i + 50, j + 50, fill="light blue", outline="#f0f0f0", width=3, tags="cell")
                cells[((i, i + 50), (j, j + 50))] = cell

        # creating a transp 35x35 pixel square (default value for the layer of images)
        transp_sq = Image.new("RGBA", (35, 35),  (255, 255, 255, 0))
        transp_sq = ImageTk.PhotoImage(transp_sq)

        # creating the image layer - 2nd - to display droplet and eggplant images
        images = {}
        for i in range(27, 527, 50):
            for j in range(27, 527, 50):
                cell = canvas.create_image(i, j, image=transp_sq, anchor=tk.CENTER, tags="img")
                images[(i, j)] = cell

        # creating the layer of text - 3rd - to display the number of mines
        text = {}
        for i in range(27, 527, 50):
            for j in range(27, 527, 50):
                cell = canvas.create_text(i, j, text="", font=("Bahnschrift", 16, "bold"), fill="white", anchor=tk.CENTER, tags="txt")
                text[(i, j)] = cell

        # main window centering
        root.eval('tk::PlaceWindow . center')

        # disabling main window resizing
        root.resizable(False, False)

        # intercepting click on the cross
        root.protocol("WM_DELETE_WINDOW", push_exit)

        # disabling submenu tearing off
        root.option_add("*tearOff", False)

        # menu configuration
        main_menu = tk.Menu()
        level_menu = tk.Menu()
        main_menu.add_cascade(label="Level", menu=level_menu)
        var_lvl = tk.StringVar(value=level[0])
        level_menu.add_radiobutton(label="10 dicks", variable=var_lvl, command=lambda : set_level("10 dicks"))
        level_menu.add_radiobutton(label="15 dicks", variable=var_lvl, command=lambda : set_level("15 dicks"))
        level_menu.add_radiobutton(label="20 dicks", variable=var_lvl, command=lambda : set_level("20 dicks"))
        sounds_menu = tk.Menu()
        main_menu.add_cascade(label="Sounds", menu=sounds_menu)
        sounds_menu.add_checkbutton(label="Mute", variable=mute, command=mute_func)
        records_menu = tk.Menu()
        main_menu.add_cascade(label="Records", menu=records_menu)
        records_menu.add_command(label="Show table", command=show_records)
        root.config(menu=main_menu)

        # creating and packing labels for status bar and session time bar
        status_bar_left = tk.Label(root, text=f"Welcome to the party! First move is safe!", anchor=tk.W)
        status_bar_left.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        session_time_right = tk.Label(root, anchor=tk.E, width=7)
        session_time_right.pack(side=tk.RIGHT, anchor=tk.E, padx=5)

        # creating PhotoImage objects from png's for displaying dropplets and eggplants
        try:
            dropplets_img = ImageTk.PhotoImage(Image.open(resource_path("images/droplets.png")))
            eggplant_img = ImageTk.PhotoImage(Image.open(resource_path("images/eggplant.png")))
        except FileNotFoundError:
            messagebox.showerror("Error", "Image files for mines and tags were not found in the directory.\nThe game will be terminated.")
            root.destroy()
            exit = not exit

        # inf loop for the run_app (exit if exit == True)
        root.mainloop()


if __name__ == "__main__":
    main()