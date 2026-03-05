from legacy_classes import GameField
import sys
import os
import tkinter as tk
from tkinter import ttk
import pygame.mixer
from random import choice


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

def get_init_field(level):
    new_field = GameField(10, level[1])
    new_field.init_field()
    return new_field

def resource_path(relative_path):
    try:
        # pyinstaller creating the temp dir and keeping the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # launch from the program folder (onedir mode)
        base_path = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_recordsmen(levels):
    try:
        recordsmen = {}
        with open(resource_path("records.txt"), 'r', encoding="utf-8") as records:
            for lvl in levels:
                recordsmen[lvl] = tuple(records.readline().rstrip().split(", "))
    except FileNotFoundError:
        pass
    else:
        return recordsmen
    
def show_records(root, levels_, mute):
    recordsmen = get_recordsmen(levels_)

    if recordsmen:
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

        level_names = tuple(levels_)
        recordsmen_values = [list(x) for x in list(recordsmen.values())]
        recordsmen_lst = [[level_names[i]] + recordsmen_values[i] for i in range(3)]

        # insert data into the Treeview
        for item in recordsmen_lst:
        # "" means no parent (top level item), "end" means insert at the end of the list
            tree.insert("", tk.END, values=item)

        play_sound(mute, "do_you_like", pool=False)

        # pack the widgets
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)


def play_sound(mute, mode, pool=True):
    if not mute:
        prefix, postfix = "sounds/", ".mp3"
        try:
            if pool:
                match mode:
                    case "lose":
                        fix = choice(("aaah", "victim", "augh", "fuck_you", "leather_man", "lube_it_up", "suction"))
                    case "move":
                        fix = choice(("thats_amazing", "yes", "spank_1", "spank_2", "spank_3", "woo"))
                    case "start":
                        fix = choice(("lash", "make_me_cum", "that_turns_me_on", "stick_finger"))
                    case "tag":
                        fix = choice(("ass_we_can", "fucking_deep", "mmmm", "eargasm_1", "eargasm_2"))
                    case "win":
                        fix = choice(("celebrate", "dungeon_master", "wee_wee"))
            else:
                fix = mode
            pygame.mixer.music.load(resource_path(prefix + fix + postfix))
            pygame.mixer.music.play()
        except FileNotFoundError:
            pass