import canvas_related as cr
import common_logics as cl
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import pygame.mixer
from random import choice
import time
import os
import stat


def main():
    exit, mute, start = False, False, None
    target_cell, prev_cell = None, None
    levels = {"10 dicks" : 10, "15 dicks" : 15, "20 dicks" : 20}
    level = tuple(levels.items())[0]

    while not exit:
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
                                field = cl.get_init_field(level)
                                if not field.field[i][j].is_mine:
                                    cell = field.field[i][j]
                                    break
                        closed_before = field.closed
                        field.open_cell(i, j)
                        cr.fill_opened_cells(field, canvas, all=False)
                        if cell.is_mine:
                            lose_win("lose")
                        else:
                            if field.closed == field.total_mines:
                                lose_win("win")
                            else:
                                if closed_before - field.closed > 1:
                                    cl.play_sound(mute, "nice", pool=False)
                                else:
                                    cl.play_sound(mute, "move")
                                cr.show_open(field, canvas, droplets_img, eggplant_img, transp_sq, mode="show")
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
                        cl.play_sound(mute, "tag")
                        cr.show_open(field, canvas, droplets_img, eggplant_img, transp_sq, mode="show")
                        status_bar_left.config(text=f"The tag is {"" if cell.is_tagged else "un"}set! Tags set: {field.tags}. Cells left to open: {field.closed - field.total_mines}.")

        def lose_win(message):
            nonlocal exit, level, start
            recordsmen = cl.get_recordsmen(levels)

            cl.play_sound(mute, message)
            cr.show_open(field, canvas, droplets_img, eggplant_img, transp_sq, mode="open")

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
                        os.chmod(cl.resource_path("records.txt"), stat.S_IWRITE)
                        with open(cl.resource_path("records.txt"), 'r+', encoding="utf-8") as records:
                            records.truncate()
                            values_as_strings = [", ".join(x) + "\n" for x in recordsmen.values()]
                            st_to_write = "".join(values_as_strings).rstrip("\n")
                            records.writelines(st_to_write)
                        os.chmod(cl.resource_path("records.txt"), 0o444)
                    except FileNotFoundError as error:
                        messagebox.showerror("Error", error)

            result = messagebox.askyesno("Game over", f"You {message}! Wish you try once more?")
            if not result:
                exit = True  # Exit the loop if "No" is pressed
            start = None
            root.destroy()

        # event handler - "cursor hovers over a closed cell"
        def on_motion(event):
            #=^.^=
            nonlocal target_cell, prev_cell
            cell_table = cl.get_table(1, True)
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
                
        def push_exit():
            nonlocal exit
            result = messagebox.askyesno("Exit", "Are you sure you want to quit?")
            if result:
                root.destroy()
                exit = True  # Exit the loop if "Yes" is pressed

        def mute_func():
            nonlocal mute
            mute = not mute
        
        def set_level(value : str):
            nonlocal level
            level = (value, levels[value])
            root.destroy()

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

        def get_secs_from_hhmmss(hhmmss : str):
            parse_time = [int(x) for x in hhmmss.split(":")]
            return parse_time[0] * 3600 + parse_time[1] * 60 + parse_time[2]
        
        def get_time_in_hhmmss():
            return time.strftime("%H:%M:%S", time.gmtime(time.time() - start))
        
        # getting the reverse lookup table for the image layer - to determine the cell that was clicked
        img_table_rvrs = cl.get_table(101, True)

        # mixer initialization (if mute == False)
        if not mute:
            pygame.mixer.init()
        
        # greeting, sound accompaniment
        cl.play_sound(mute, mode="start")

        # field creating + initialization, default level = "Easy / 10 mines"
        field = cl.get_init_field(level)

        # main window, creating + configuration
        root = tk.Tk()
        root.title("Men's♂wee-weeper")
        root.geometry("510x560")
        try:
            root.iconbitmap(default=cl.resource_path("images/darkholme.ico"))
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

        # creating PhotoImage objects from png's for displaying dropplets and eggplants
        droplets_img = ImageTk.PhotoImage(Image.open(cl.resource_path("images/droplets.png")))
        eggplant_img = ImageTk.PhotoImage(Image.open(cl.resource_path("images/eggplant.png")))

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
        records_menu.add_command(label="Show table", command=lambda : cl.show_records(root, levels, mute))
        root.config(menu=main_menu)

        # creating and packing labels for status bar and session time bar
        status_bar_left = tk.Label(root, text=f"Welcome to the party! First move is safe!", anchor=tk.W)
        status_bar_left.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        session_time_right = tk.Label(root, anchor=tk.E, width=7)
        session_time_right.pack(side=tk.RIGHT, anchor=tk.E, padx=5)

        # inf loop for the run_app (exit if exit == True)
        root.mainloop()

if __name__ == "__main__":
    main()