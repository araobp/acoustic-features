# << Logger GUI >>
#
# This implementaion makes use of matplotlib on Tk for agile GUI development.
#
# Reference: https://matplotlib.org/2.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html
#

import matplotlib
matplotlib.use('TkAgg')

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sys
import tkinter as Tk
from datetime import datetime
import time
import os

import matplotlib.pyplot as plt

import dataset
import asc

# Command arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="serial port identifier")
parser.add_argument("-d", "--dataset_folder",
                    help="Data folder for saving feature data from the device")
parser.add_argument("-t", "--time", help="measurement time")
parser.add_argument("-s", "--section", help="section")

args = parser.parse_args()

if __name__ == '__main__':

    ds = dataset.DataSet(args.dataset_folder)
    num_classes = len(ds.class_labels)

    TIME = int(args.time)
    NUM_SECTION = int(args.section)

    asc = asc.ASC(args.port, ds)

    PADX = 6
    PADX_GRID = 2
    PADY_GRID = 2
    WIDTH = 7
    BG = 'darkturquoise'

    root = Tk.Tk()
    root.wm_title("Logger")

    fig, ax = plt.subplots(1, 1, figsize=(11, 5))        
    fig.subplots_adjust(bottom=0.3)
    
    frame = Tk.Frame(master=root)
    frame_row0 = Tk.Frame(master=frame)
    frame_row1 = Tk.Frame(master=frame)
    frame_row2 = Tk.Frame(master=frame)
    
    canvas = FigureCanvasTkAgg(fig, master=frame_row0)
    canvas.draw()

    def asc_stats():
        global fig, canvas, repeat_action
        finished = asc.plot(ax, 'stats', TIME, NUM_SECTION)
        fig.tight_layout()
        canvas.draw()
        if finished:
            repeat_action = False
        else:
            repeat(asc_stats)

    def asc_life_log():
        global fig, canvas, repeat_action
        finished = asc.plot(ax, 'life_log', TIME, NUM_SECTION)
        fig.tight_layout()
        canvas.draw()
        if finished:
            repeat_action = False
        else:
            repeat(asc_life_log)

    def repeat(func):
        global repeat_action
        if repeat_action:
            root.after(50, func)

    def start_stats():
        global repeat_action
        repeat_action = True
        repeat(asc_stats)

    def start_life_log():
        global repeat_action
        repeat_action = True
        repeat(asc_life_log)

    def stop():
        global repeat_action
        repeat_action = False

    def savefig():
        global fig
        fig.savefig('log.png')

    def quit():
        root.quit()
        root.destroy()

    ##### GUI components #####

    button_stats = Tk.Button(master=frame_row1, text='Stats', command=start_stats,
                        bg=BG, activebackground='grey', padx=PADX, width=WIDTH)

    button_life_log = Tk.Button(master=frame_row1, text='Life log', command=start_life_log,
                        bg=BG, activebackground='grey', padx=PADX, width=WIDTH)

    button_stop = Tk.Button(master=frame_row1, text='Stop', command=stop,
                        bg=BG, activebackground='grey', padx=PADX, width=WIDTH)

    button_savefig = Tk.Button(master=frame_row2, text='Savefig', command=savefig,
                        bg=BG, activebackground='grey', padx=PADX, width=WIDTH)

    button_quit = Tk.Button(master=frame_row2, text='Quit', command=quit,
                        bg='yellow', activebackground='grey', padx=PADX, width=WIDTH)

    ##### Place the parts on Tk #####
    frame.pack(expand=True, fill=Tk.BOTH)

    ### Row 0: main canvas
    frame_row0.pack(expand=True, fill=Tk.BOTH)
    canvas._tkcanvas.pack(expand=True, fill=Tk.BOTH)

    ### Row 1: operation ####
    button_stats.grid(row=0, column=0, padx=PADX_GRID)
    button_life_log.grid(row=0, column=1, padx=PADX_GRID)
    button_stop.grid(row=0, column=2, padx=PADX_GRID)
    frame_row1.pack(pady=PADY_GRID)

    ### Row 2 ####
    button_savefig.grid(row=0, column=0, padx=PADX_GRID)
    button_quit.grid(row=0, column=1, padx=PADX_GRID)
    frame_row2.pack(pady=PADY_GRID)

    ##### loop forever #####
    Tk.mainloop()
