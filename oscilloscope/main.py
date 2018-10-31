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

import matplotlib.pyplot as plt
plt.style.use('dark_background')

matplotlib.use('TkAgg')

CMAP_LIST = ['hot',
             'ocean',
             'binary',
             'cubehelix',
             'magma',
             'viridis',
             'winter',
             'summer',
             'cool',
             'gray']

root = Tk.Tk()
root.wm_title("Oscilloscope")

f = Figure(figsize=(9, 4), dpi=100)
ax = f.add_subplot(111)

canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

entry = Tk.Entry(master=root, width=16)
cmap = Tk.Spinbox(master=root, width=12, values=CMAP_LIST)
counter = Tk.Label(master=root)
range_amplitude = Tk.Spinbox(master=root, width=6, values=[2**8, 2**9, 2**11, 2**13, 2**15])
range_filtered = Tk.Spinbox(master=root, width=3, values=[int(dsp.NUM_FILTERS*0.6), int(dsp.NUM_FILTERS*.8), dsp.NUM_FILTERS])
range_filtered_l = Tk.Spinbox(master=root, width=4, values=[int(dsp.NUM_FILTERS_L*0.4), int(dsp.NUM_FILTERS_L*.7), dsp.NUM_FILTERS_L])
range_mfcc = Tk.Spinbox(master=root, width=3, values=[13, 18, 25])

cnt = 0
class_label_ = ''
counter.configure(text='({})'.format(str(0)))

repeat_action = False

def df_save(df, step):
    global class_label_, cnt
    class_label = entry.get()
    if class_label != '':
        dt = datetime.today().strftime('%Y%m%d%H%M%S')
        filename = '{}-{}-{}.csv'.format(entry.get(), step, dt)
        df.to_csv('./data/' + filename, index=False)
        if (class_label_ != class_label):
            class_label_ = class_label
            cnt = 0
        cnt += 1
        counter.configure(text='({})'.format(str(cnt)))

def repeat(func):
    if repeat_action:
        root.after(100, func)

def raw_wave():
    dsp.range_waveform = int(range_amplitude.get())
    ax.clear()
    ax.grid(True, alpha=0.3)
    df = dsp.serial_read(dsp.RAW_WAVE)
    dsp.plot_aed(ax, df, dsp.RAW_WAVE)
    canvas.draw()
    df_save(df, 'waveform')
    repeat(raw_wave)

def psd():
    ax.clear()
    ax.grid(True, alpha=0.3)
    df = dsp.serial_read(dsp.PSD)
    dsp.plot_aed(ax, df, dsp.PSD)
    canvas.draw()
    df_save(df, 'psd')
    repeat(psd)

def filtered_mel():
    dsp.range_filtered = int(range_filtered.get())
    dsp.cmap = cmap.get()
    ax.clear()
    df = dsp.serial_read(dsp.FILTERED_MEL)
    dsp.plot_aed(ax, df, dsp.FILTERED_MEL)
    canvas.draw()
    df_save(df, 'melpsd')
    repeat(filtered_mel)

def filtered_linear():
    dsp.range_filtered = int(range_filtered_l.get())
    dsp.cmap = cmap.get()
    ax.clear()
    df = dsp.serial_read(dsp.FILTERED_LINEAR)
    dsp.plot_aed(ax, df, dsp.FILTERED_LINEAR)
    canvas.draw()
    df_save(df, 'linearpsd')
    repeat(filtered_linear)

def mfcc():
    dsp.range_mfcc = int(range_mfcc.get())
    dsp.cmap = cmap.get()
    ax.clear()
    df = dsp.serial_read(dsp.MFCC)
    dsp.plot_aed(ax, df, dsp.MFCC)
    canvas.draw()
    df_save(df, 'mfcc')
    repeat(mfcc)

def repeat_toggle():
    global repeat_action
    if repeat_action == True:
        repeat_action = False
    else:
        repeat_action = True
    
def on_key_event(event):
    print('you pressed %s' % event.key)
    key = event.key
    m = None
    if (key == '1'):
        raw_wave()
    elif (key == '2'):
        psd()
    elif (key == '3'):
        filtered_mel()
    elif (key == '4'):
        filtered_linear()
    elif (key == '5'):
        mfcc()
    key_press_handler(event, canvas)

canvas.mpl_connect('key_press_event', on_key_event)

def _quit():
    root.quit()
    root.destroy()

label_class = Tk.Label(master=root, text='Class label:')
label_cmap = Tk.Label(master=root, text='cmap:')

button_waveform = Tk.Button(master=root, text='Wave', command=raw_wave, bg='lightblue', activebackground='grey')
button_psd = Tk.Button(master=root, text='FFT', command=psd, bg='lightblue', activebackground='grey')
button_filtered_linear = Tk.Button(master=root, text='Spectrogram', command=filtered_linear, bg='lightblue', activebackground='grey')
button_filtered_mel = Tk.Button(master=root, text='Spectrogram(mel)', command=filtered_mel, bg='pink', activebackground='grey')
button_mfcc = Tk.Button(master=root, text='MFCCs', command=mfcc, bg='yellowgreen', activebackground='grey')
button_repeat = Tk.Button(master=root, text='Repeat', command=repeat_toggle, bg='lightblue', activebackground='grey')
button_quit = Tk.Button(master=root, text='Quit', command=_quit, bg='yellow', activebackground='grey')

# Class label entry
label_class.pack(side=Tk.LEFT, padx=1, pady=10)
entry.pack(side=Tk.LEFT, padx=1)
counter.pack(side=Tk.LEFT, padx=1)
label_seperator1 = Tk.Label(master=root, text=' ')
label_seperator1.pack(side=Tk.LEFT, padx=1)

# Waveform
range_amplitude.pack(side=Tk.LEFT, padx=1)
button_waveform.pack(side=Tk.LEFT, padx=1)
label_seperator2 = Tk.Label(master=root, text=' ')
label_seperator2.pack(side=Tk.LEFT, padx=1)

# FFT (PSD)
button_psd.pack(side=Tk.LEFT, padx=1)
label_seperator3 = Tk.Label(master=root, text=' ')
label_seperator3.pack(side=Tk.LEFT, padx=1)

# Linear-scale Spectrogram (PSD)
range_filtered_l.pack(side=Tk.LEFT, padx=1)
button_filtered_linear.pack(side=Tk.LEFT, padx=1)
label_seperator5 = Tk.Label(master=root, text=' ')
label_seperator5.pack(side=Tk.LEFT, padx=1)

# Mel-scale Spectrogram (PSD)
range_filtered.pack(side=Tk.LEFT, padx=1)
button_filtered_mel.pack(side=Tk.LEFT, padx=1)
label_seperator4 = Tk.Label(master=root, text=' ')
label_seperator4.pack(side=Tk.LEFT, padx=1)

# MFCC
range_mfcc.pack(side=Tk.LEFT, padx=1)
button_mfcc.pack(side=Tk.LEFT, padx=1)
label_seperator6 = Tk.Label(master=root, text=' ')
label_seperator6.pack(side=Tk.LEFT, padx=1)

# CMAP
label_cmap.pack(side=Tk.LEFT, padx=1)
cmap.pack(side=Tk.LEFT, padx=1)
label_seperator6 = Tk.Label(master=root, text=' ')
label_seperator6.pack(side=Tk.LEFT, padx=1)

# Repeat
button_repeat.pack(side=Tk.LEFT, padx=1)

# Quit
button_quit.pack(side=Tk.LEFT, padx=15)

Tk.mainloop()
