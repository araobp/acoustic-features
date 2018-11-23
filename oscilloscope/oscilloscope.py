#!/usr/bin/env python3

# Reference: https://matplotlib.org/2.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html

import matplotlib
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import sys
import tkinter as Tk
import dsp
from datetime import datetime
import time
import os

import matplotlib.pyplot as plt
plt.style.use('dark_background')

dsp.port = sys.argv[1]

### Default settings to DSP ###
dsp.set_beam_forming('e', 'c')  # ENDFIRE mode, center
dsp.enable_pre_emphasis(True)  # Pre emphasis enabled
###############################

matplotlib.use('TkAgg')

CMAP_LIST = ['hot',
             'viridis',
             'gray',
             'binary',
             'ocean',
             'magma',
             'cubehelix',
             'cool',
             'winter',
             'summer']

root = Tk.Tk()
root.wm_title("Oscilloscope")

fig = Figure(figsize=(9, 4), dpi=100)
ax = fig.add_subplot(111)
fig.subplots_adjust(bottom=0.15)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

entry = Tk.Entry(master=root, width=14)
cmap = Tk.Spinbox(master=root, width=10, values=CMAP_LIST)
counter = Tk.Label(master=root)
range_amplitude = Tk.Spinbox(master=root, width=6, values=[2**8, 2**9, 2**11, 2**13, 2**15])
range_filtered = Tk.Spinbox(master=root, width=3, values=[dsp.NUM_FILTERS, int(dsp.NUM_FILTERS*.8), int(dsp.NUM_FILTERS*0.6)])
range_filtered_l = Tk.Spinbox(master=root, width=4, values=[dsp.NUM_FILTERS_L, int(dsp.NUM_FILTERS_L*.7), int(dsp.NUM_FILTERS_L*0.4)])
range_mfcc = Tk.Spinbox(master=root, width=3, values=[25, 18, 13])
mode_beam_forming = Tk.Spinbox(master=root, width=2, values=['e', 'b'])
range_beam_forming = Tk.Spinbox(master=root, width=2, values=['c', 'r', 'R', 'l', 'L'])
spectrum_subtraction = Tk.Spinbox(master=root, width=3, values=[0, 10, 15, 20, 25])

cnt = 0
class_label_ = ''
counter.configure(text='({})'.format(str(0)))

repeat_action = False

filename = None

def df_save(df, step):
    global class_label_, cnt, filename
    class_label = entry.get()
    dt = datetime.today().strftime('%Y%m%d%H%M%S')
    if class_label == '':
        filename = './data/{}-{}'.format(step, dt)
    else:
        filename = './data/{}-{}-{}'.format(entry.get(), step, dt)
        df.to_csv(filename+'.csv', index=False)
        if (class_label_ != class_label):
            class_label_ = class_label
            cnt = 0
        cnt += 1
        counter.configure(text='({})'.format(str(cnt)))

def repeat(func):
    if repeat_action:
        root.after(50, func)

def raw_wave():
    dsp.range_waveform = int(range_amplitude.get())
    ax.clear()
    ax.grid(True, alpha=0.3)
    df = dsp.serial_read(dsp.RAW_WAVE)
    dsp.plot_aed(ax, df, dsp.RAW_WAVE)
    canvas.draw()
    df_save(df, 'waveform')
    repeat(raw_wave)

def fft():
    dsp.ssub = int(spectrum_subtraction.get())
    ax.clear()
    ax.grid(True, alpha=0.3)
    df = dsp.serial_read(dsp.PSD)
    dsp.plot_aed(ax, df, dsp.PSD)
    canvas.draw()
    df_save(df, 'fft')
    repeat(fft)

def filtered_mel():
    dsp.ssub = int(spectrum_subtraction.get())
    dsp.range_filtered = int(range_filtered.get())
    dsp.cmap = cmap.get()
    ax.clear()
    df = dsp.serial_read(dsp.FILTERED_MEL)
    dsp.plot_aed(ax, df, dsp.FILTERED_MEL)
    canvas.draw()
    df_save(df, 'mel_spectrogram')
    repeat(filtered_mel)

def filtered_linear():
    dsp.ssub = int(spectrum_subtraction.get())    
    dsp.range_filtered = int(range_filtered_l.get())
    dsp.cmap = cmap.get()
    ax.clear()
    df = dsp.serial_read(dsp.FILTERED_LINEAR)
    dsp.plot_aed(ax, df, dsp.FILTERED_LINEAR)
    canvas.draw()
    df_save(df, 'spectrogram')
    repeat(filtered_linear)

def mfcc():
    dsp.ssub = int(spectrum_subtraction.get())    
    dsp.range_mfcc = int(range_mfcc.get())
    dsp.cmap = cmap.get()
    ax.clear()
    df = dsp.serial_read(dsp.MFCC)
    dsp.plot_aed(ax, df, dsp.MFCC)
    canvas.draw()
    df_save(df, 'mfcc')
    repeat(mfcc)

def beam_forming():
    mode = mode_beam_forming.get()
    angle = range_beam_forming.get()
    dsp.set_beam_forming(mode, angle)

def repeat_toggle():
    global repeat_action
    if repeat_action == True:
        repeat_action = False
        button_repeat.configure(bg='lightblue')
    else:
        repeat_action = True
        button_repeat.configure(bg='red')
        
def pre_emphasis_toggle():
    if button_pre_emphasis.cget('bg') == 'lightblue':
        button_pre_emphasis.configure(bg='red')
        dsp.enable_pre_emphasis(True)
    else:       
        button_pre_emphasis.configure(bg='lightblue')
        dsp.enable_pre_emphasis(False)
        
def savefig():
    global filename
    if filename:
        fig.savefig(filename+'.png')

def remove():
    global filename, cnt
    if filename:
        os.remove(filename+'.csv')
        cnt -= 1
        counter.configure(text='({})'.format(str(cnt)))
    
def on_key_event(event):
    print('you pressed %s' % event.key)
    key = event.key
    m = None
    if (key == 'w'):
        raw_wave()
    elif (key == 'f'):
        fft()
    elif (key == 'm'):
        filtered_mel()
    elif (key == 's'):
        filtered_linear()
    elif (key == 'c'):
        mfcc()
    key_press_handler(event, canvas)

canvas.mpl_connect('key_press_event', on_key_event)

def _quit():
    root.quit()
    root.destroy()

label_class = Tk.Label(master=root, text='Class label')
label_image = Tk.Label(master=root, text='image')

button_waveform = Tk.Button(master=root, text='Wave', command=raw_wave, bg='lightblue', activebackground='grey')
button_psd = Tk.Button(master=root, text='FFT', command=fft, bg='lightblue', activebackground='grey')
button_filtered_linear = Tk.Button(master=root, text='Spec', command=filtered_linear, bg='lightblue', activebackground='grey')
button_filtered_mel = Tk.Button(master=root, text='Mel spec', command=filtered_mel, bg='pink', activebackground='grey')
button_mfcc = Tk.Button(master=root, text='MFCCs', command=mfcc, bg='yellowgreen', activebackground='grey')
button_beam_forming = Tk.Button(master=root, text='Beam', command=beam_forming, bg='lightblue', activebackground='grey')

button_repeat = Tk.Button(master=root, text='Repeat', command=repeat_toggle, bg='lightblue', activebackground='grey')
button_pre_emphasis = Tk.Button(master=root, text='Emphasis', command=pre_emphasis_toggle, bg='red', activebackground='grey')
button_savefig = Tk.Button(master=root, text='Savefig', command=savefig, bg='lightblue', activebackground='grey')
button_remove = Tk.Button(master=root, text='Remove', command=remove, bg='lightblue', activebackground='grey')

button_quit = Tk.Button(master=root, text='Quit', command=_quit, bg='yellow', activebackground='grey')

# Class label entry
label_class.pack(side=Tk.LEFT, padx=1, pady=10)
entry.pack(side=Tk.LEFT, padx=1)
counter.pack(side=Tk.LEFT, padx=1)
label_separator1 = Tk.Label(master=root, text=' ')
label_separator1.pack(side=Tk.LEFT, padx=1)

# Waveform
range_amplitude.pack(side=Tk.LEFT, padx=1)
button_waveform.pack(side=Tk.LEFT, padx=1)
label_separator2 = Tk.Label(master=root, text=' ')
label_separator2.pack(side=Tk.LEFT, padx=1)

# FFT (PSD)
button_psd.pack(side=Tk.LEFT, padx=1)
label_separator3 = Tk.Label(master=root, text=' ')
label_separator3.pack(side=Tk.LEFT, padx=1)

# Linear-scale Spectrogram (PSD)
range_filtered_l.pack(side=Tk.LEFT, padx=1)
button_filtered_linear.pack(side=Tk.LEFT, padx=1)
label_separator5 = Tk.Label(master=root, text=' ')
label_separator5.pack(side=Tk.LEFT, padx=1)

# Mel-scale Spectrogram (PSD)
range_filtered.pack(side=Tk.LEFT, padx=1)
button_filtered_mel.pack(side=Tk.LEFT, padx=1)
label_separator4 = Tk.Label(master=root, text=' ')
label_separator4.pack(side=Tk.LEFT, padx=1)

# MFCC
range_mfcc.pack(side=Tk.LEFT, padx=1)
button_mfcc.pack(side=Tk.LEFT, padx=1)
label_separator6 = Tk.Label(master=root, text=' ')
label_separator6.pack(side=Tk.LEFT, padx=1)

# Beam forming
mode_beam_forming.pack(side=Tk.LEFT, padx=1)
range_beam_forming.pack(side=Tk.LEFT, padx=1)
button_beam_forming.pack(side=Tk.LEFT, padx=1)
label_separator7 = Tk.Label(master=root, text=' ')
label_separator7.pack(side=Tk.LEFT, padx=1)

# CMAP
label_image.pack(side=Tk.LEFT, padx=1)
spectrum_subtraction.pack(side=Tk.LEFT, padx=1)
cmap.pack(side=Tk.LEFT, padx=1)
label_separator8 = Tk.Label(master=root, text=' ')
label_separator8.pack(side=Tk.LEFT, padx=1)

# Repeat, pre_emphasis, save fig and delete
button_repeat.pack(side=Tk.LEFT, padx=1)
button_pre_emphasis.pack(side=Tk.LEFT, padx=1)
button_savefig.pack(side=Tk.LEFT, padx=1)
button_remove.pack(side=Tk.LEFT, padx=1)

# Quit
button_quit.pack(side=Tk.LEFT, padx=15)

Tk.mainloop()
