# << Oscilloscope GUI >>
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

import dsp
import gui
import yaml
import dataset

CMAP_LIST = ('hot',
             'viridis',
             'gray',
             'magma',
             'cubehelix',
             'BrBG',
             'RdBu',
             'bwr',
             'coolwarm',
             'seismic')

# Command arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("port", help="serial port identifier")
parser.add_argument("-D", "--debug",
                    help="serial port identifier",
                    action="store_true")
parser.add_argument("-d", "--dataset_folder",
                    help="Data folder for saving feature data from the device",
                    default='.')
parser.add_argument("-b", "--browser",
                    help="Data browser", action="store_true")
parser.add_argument("-s", "--plot_style",
                    help="Plot style", default='dark_background')
parser.add_argument("-o", "--oscilloscope_mode",
                    help="Oscilloscope mode", action="store_true")
parser.add_argument("-f", "--fullscreen_mode",
                    help="Fullscreen mode", default=None)
parser.add_argument("-c", "--color_map",
                    help="Color map", default=','.join(CMAP_LIST))
args = parser.parse_args()

if __name__ == '__main__':

    dataset = dataset.DataSet(args.dataset_folder)
    class_file = args.dataset_folder + '/class_labels.yaml'

    plt.style.use(args.plot_style)

    itfc = dsp.Interface(port=args.port, dataset=dataset)
        
    # Beam forming mode
    mode = dsp.ENDFIRE

    ### Default settings to DSP ###
    itfc.set_beam_forming(mode, 'c')  # ENDFIRE mode, center
    itfc.enable_pre_emphasis(True)  # Pre emphasis enabled
    ###############################

    PADX = 6
    PADX_GRID = 2
    PADY_GRID = 2
    WIDTH = 7
    BG = 'darkturquoise'
    
    ANGLE = ('L', 'l', 'c', 'r', 'R')
    
    cmap_list = args.color_map.split(',')

    cnt = 0
    repeat_action = False
    
    current_class_label = ''
    filename = None
    data = None
    cnn_model = None
    last_operation = None

    EMPTY = np.array([])

    gui = gui.GUI(interface=itfc, dataset=dataset, fullscreen=args.fullscreen_mode)

    if dataset.model and not args.browser:
        import inference
        cnn_model = inference.Model(dataset)

    root = Tk.Tk()
    if args.fullscreen_mode:
        root.wm_title("")
    else:
        root.wm_title("Oscilloscope and spectrum analyzer for deep learning")

    if args.browser:
        fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    else:
        fig, ax = plt.subplots(1, 1, figsize=(11, 4))        
    fig.subplots_adjust(bottom=0.15)
    
    frame = Tk.Frame(master=root)
    frame_row0 = Tk.Frame(master=frame)
    frame_row0a = Tk.Frame(master=frame_row0)
    frame_row0b = Tk.Frame(master=frame_row0, padx=PADX)
    frame_row1 = Tk.Frame(master=frame)
    frame_row2 = Tk.Frame(master=frame)
    frame_row3 = Tk.Frame(master=frame)
    frame_row4 = Tk.Frame(master=frame)
    
    canvas = FigureCanvasTkAgg(fig, master=frame_row0a)
    canvas.draw()

    # Save training data for deep learning
    def save():
        global current_class_label, cnt, filename
        class_label = entry_class_label.get()
        func, data, window, pos = last_operation
        angle = range_beam_forming.get()
        dt = datetime.today().strftime('%Y%m%d%H%M%S')
        if args.dataset_folder:
            dataset_folder = args.dataset_folder
        else:
            dataset_folder = './data'

        if class_label == '':
            filename = dataset_folder+'/data/{}-{}'.format(dt, func.__name__)
        else:
            if func == mfsc or func == mfcc:  # Save both data at a time
                filename = dataset_folder+'/data/{}-features-{}-{}-{}'.format(dt, class_label, pos, ANGLE[angle+2])
            else:
                filename = dataset_folder+'/data/{}-{}-{}'.format(dt, class_label, func.__name__)
            data = data.flatten()
            with open(filename+'.csv', "w") as f:
                f.write(','.join(data.astype(str)))

            if current_class_label != class_label:
                current_class_label = class_label
                cnt = 0
            cnt += 1
            counter.configure(text='({})'.format(str(cnt)))

    def repeat(func):
        global repeat_action
        if repeat_action:
            root.after(50, func)

    def infer(data, pos=None):
        if pos is None:
            pos = 0
        probabilities = cnn_model.infer(data)
        class_label, p = probabilities[pos][0]
        label_inference.configure(text='This is {} ({} %)'.format(class_label, int(p)))
        
    def raw_wave(repeatable=True):
        global last_operation
        range_ = int(range_amplitude.get())
        data = gui.plot(ax, dsp.RAW_WAVE, range_=range_)
        last_operation = (raw_wave, data, None, None)
        fig.tight_layout()
        canvas.draw()
        if repeatable:
            repeat(raw_wave)

    def fft(repeatable=True):
        global last_operation
        ssub = int(spectrum_subtraction.get())
        data = gui.plot(ax, dsp.FFT)
        last_operation = (fft, data, None, None)
        fig.tight_layout()
        canvas.draw()
        if repeatable:
            repeat(fft)

    def spectrogram(data=EMPTY, pos=0, repeatable=True):
        global last_operation, dataset
        ssub = int(spectrum_subtraction.get())    
        range_ = int(range_spectrogram.get())
        cmap_ = var_cmap.get()
        if data is EMPTY:
            window = dataset.windows[int(range_window.get())]
            data = gui.plot(ax, dsp.SPECTROGRAM, range_, cmap_, ssub)
        else:
            window = dataset.windows[pos]
            gui.plot(ax, dsp.SPECTROGRAM, range_, cmap_, ssub, data=data,
                         window=None)
        last_operation = (spectrogram, data, window, pos)
        fig.tight_layout()
        canvas.draw()
        if repeatable:
            repeat(spectrogram)

    def mfsc(data=EMPTY, pos=None, repeatable=True):
        global last_operation, dataset
        print(pos)
        ssub = int(spectrum_subtraction.get())
        range_ = int(range_mfsc.get())
        cmap_ = var_cmap.get()
        if data is EMPTY:
            window = dataset.windows[int(range_window.get())]
            data = gui.plot(ax, dsp.MFSC, range_, cmap_, ssub,
                               window=window)
        else:
            window = dataset.windows[pos] if pos else None
            gui.plot(ax, dsp.MFSC, range_, cmap_, ssub, data=data,
                         window=window)
        if cnn_model:
            infer(data, pos)
        last_operation = (mfsc, data, window, pos)
        fig.tight_layout()
        canvas.draw()
        if repeatable:
            repeat(mfsc)

    def mfcc(data=EMPTY, pos=None, repeatable=True):
        global last_operation, dataset
        ssub = int(spectrum_subtraction.get())    
        range_ = int(range_mfcc.get())
        cmap_ = var_cmap.get()
        if data is EMPTY:
            window = dataset.windows[int(range_window.get())]
            data = gui.plot(ax, dsp.MFCC, range_, cmap_, ssub,
                               window=window)
        else:
            window = dataset.windows[pos] if pos else None
            window = dataset.windows[pos]
            gui.plot(ax, dsp.MFCC, range_, cmap_, ssub, data=data,
                         window=window)
        if cnn_model:
            infer(data, pos)
        last_operation = (mfcc, data, window, pos)
        fig.tight_layout()
        canvas.draw()
        if repeatable:
            repeat(mfcc)

    def welch():
        gui.plot_welch(ax)
        fig.tight_layout()
        canvas.draw()

    def beam_forming(angle):
        global mode
        angle = int(angle) + 2
        itfc.set_beam_forming(mode, ANGLE[angle])

    def repeat_toggle():
        global repeat_action
        if repeat_action == True:
            repeat_action = False
            button_repeat.configure(bg=BG)
        else:
            repeat_action = True
            button_repeat.configure(bg='red')
            
    def pre_emphasis_toggle():
        if button_pre_emphasis.cget('bg') == BG:
            button_pre_emphasis.configure(bg='red')
            itfc.enable_pre_emphasis(True)
        else:       
            button_pre_emphasis.configure(bg=BG)
            itfc.enable_pre_emphasis(False)
            
    def savefig():
        fig.savefig('screen_shot.png')

    def remove():
        global filename, cnt
        if filename:
            os.remove(filename+'.csv')
            cnt -= 1
            counter.configure(text='({})'.format(str(cnt)))

    def quit():
        root.quit()
        root.destroy()

    def confirm():
        canvas._tkcanvas.focus_set()

    def shadow(pos):
        last_operation[0](data=last_operation[1], pos=int(pos), repeatable=False)

    def filterbank():
        data = gui.plot(ax, dsp.FILTERBANK)
        canvas.draw()

    def elapsed_time():
        gui.plot(ax, dsp.ELAPSED_TIME)

    def broadside():
        global mode
        mode = dsp.BROADSIDE
        angle = range_beam_forming.get() + 2
        itfc.set_beam_forming(mode, ANGLE[angle])

    def endfire():
        global mode
        mode = dsp.ENDFIRE
        angle = int(range_beam_forming.get()) + 2
        itfc.set_beam_forming(mode, ANGLE[angle])

    def left_mic_only():
        itfc.left_mic_only()

    def right_mic_only():
        itfc.right_mic_only()

    ### Key press event ###

    def on_key_event(event):
        c = event.key
        pos = range_window.get()
        if c == 'right':
            if pos < len(dataset.windows) - 1:
                pos += 1
                range_window.set(pos)
        elif c == 'left':
            if pos > 0:
                pos -= 1
                range_window.set(pos)            
        elif c == 'up':
            if last_operation is None:
                print('Up key becomes effective after executing an operations.')
            else:
                func = last_operation[0]
                if func in (mfsc, mfcc):
                    func(pos=int(range_window.get()), repeatable=False)
                else:
                    func(repeatable=False)
        elif c == 'down':
            save()
            
        if not args.browser:
            canvas.mpl_connect('key_press_event', on_key_event)

    ### File select event ###
    def on_select(event):
        widget = event.widget
        index = int(widget. curselection()[0])
        filename = widget.get(index)
        params = filename.split('-')
        func = globals()[dataset.feature]

        with open(args.dataset_folder + '/data/' + filename) as f:
            data = np.array(f.read().split(','), dtype='float')
        
        if func == mfsc or func == mfcc:
            data = data.reshape(dataset.samples*2, dataset.filters)
            pos = params[3]
            if pos == 'a':
                func(data=data, pos=None, repeatable=False)
            else:
                func(data=data, pos=int(pos), repeatable=False)                
        else:
            data = data.reshape(dataset.samples, dataset.filters)
            func(data=data, repeatable=False)
        
    ### Row 0b ####
    if args.browser:
        list_files = Tk.Listbox(master=frame_row0b, width=30, height=20)
        files = [f for f in os.listdir(args.dataset_folder+'/data')]
        for f in files:
            list_files.insert(Tk.END, f)
        list_files.bind('<<ListboxSelect>>', on_select)
    
        scrollbar = Tk.Scrollbar(master=frame_row0b, orient="vertical")
        scrollbar.config(command=list_files.yview)
        list_files.config(yscrollcommand=scrollbar.set)
    
    ### Row 1 ####
    entry_class_label = Tk.Entry(master=frame_row1, width=14)
    var_cmap = Tk.StringVar()
    var_cmap.set(cmap_list[0])
    cmap = Tk.OptionMenu(frame_row1, var_cmap, *cmap_list)
    cmap.config(bg=BG, activebackground='paleturquoise')
    counter = Tk.Label(master=frame_row1)
    counter.configure(text='({})'.format(str(0)))
    range_amplitude = Tk.Spinbox(master=frame_row1, width=6,
                                 values=[2**8, 2**9, 2**11, 2**13, 2**15])
    range_mfsc = Tk.Spinbox(master=frame_row1, width=3,
                                       values=[dataset.filters, int(dataset.filters*.8), int(dataset.filters*0.6)])
    range_spectrogram = Tk.Spinbox(master=frame_row1, width=4,
                                   values=[int(dsp.NN/2), int(dsp.NN/2.0*.7), int(dsp.NN/2.0*0.4)])
    range_mfcc = Tk.Spinbox(master=frame_row1, width=3,
                            values=[16, 25, 40])
    spectrum_subtraction = Tk.Spinbox(master=frame_row1, width=3,
                                      values=[-60, -40, -30, -25, -20])
    label_class = Tk.Label(master=frame_row1, text='Class label:')
    label_image = Tk.Label(master=frame_row1, text='Mask:')
    label_color = Tk.Label(master=frame_row1, text='Color:')
    button_waveform = Tk.Button(master=frame_row1, text='Wave', command=raw_wave,
                                bg=BG, activebackground='grey', padx=PADX, width=WIDTH)
    button_psd = Tk.Button(master=frame_row1, text='FFT', command=fft,
                           bg=BG, activebackground='grey', padx=PADX, width=WIDTH)
    button_spectrogram = Tk.Button(master=frame_row1, text='Spec', command=spectrogram,
                                   bg=BG, activebackground='grey', padx=PADX, width=WIDTH)
    button_welch = Tk.Button(master=frame_row1, text='Welch', command=welch,
                            bg=BG, activebackground='grey', padx=PADX, width=WIDTH)
    button_mfsc = Tk.Button(master=frame_row1, text='MFSCs', command=mfsc,
                                       bg='pink', activebackground='grey', padx=PADX, width=WIDTH)
    button_mfcc = Tk.Button(master=frame_row1, text='MFCCs', command=mfcc,
                            bg='yellowgreen', activebackground='grey', padx=PADX, width=WIDTH)

    ### Row 2 ####
    button_repeat = Tk.Button(master=frame_row2, text='Repeat', command=repeat_toggle,
                              bg=BG, activebackground='grey', padx=PADX, width=WIDTH)
    button_pre_emphasis = Tk.Button(master=frame_row2, text='Emphasis', command=pre_emphasis_toggle,
                                    bg='red', activebackground='grey', padx=PADX, width=WIDTH)
    button_savefig = Tk.Button(master=frame_row2, text='Savefig', command=savefig,
                               bg=BG, activebackground='grey', padx=PADX, width=WIDTH)
    button_remove = Tk.Button(master=frame_row2, text='Remove', command=remove,
                              bg=BG, activebackground='grey', padx=PADX, width=WIDTH)
    button_save = Tk.Button(master=frame_row2, text='Save', command=save,
                              bg=BG, activebackground='grey', padx=PADX, width=WIDTH)
    button_quit = Tk.Button(master=frame_row2, text='Quit', command=quit,
                            bg='yellow', activebackground='grey', padx=PADX, width=WIDTH)
    label_beam_forming = Tk.Label(master=frame_row2, text='Beam forming:')
    label_left = Tk.Label(master=frame_row2, text='L')
    label_right = Tk.Label(master=frame_row2, text='R')
    range_beam_forming = Tk.Scale(master=frame_row2, orient=Tk.HORIZONTAL, length=70,
                                  from_=-1, to=1, showvalue=0, command=beam_forming)
    button_confirm = Tk.Button(master=frame_row2, text='Confirm', command=confirm,
                            bg=BG, activebackground='grey', padx=PADX, width=WIDTH)

    ### Row 3 ####
    button_filterbank = Tk.Button(master=frame_row3, text='Filterbank', command=filterbank,
                                  bg=BG, activebackground='grey', padx=PADX)
    button_elapsed_time = Tk.Button(master=frame_row3, text='Elapsed time', command=elapsed_time,
                                    bg=BG, activebackground='grey', padx=PADX)
    button_broadside = Tk.Button(master=frame_row3, text='Broadside', command=broadside,
                                 bg=BG, activebackground='grey', padx=PADX)
    button_endfire = Tk.Button(master=frame_row3, text='Endfire', command=endfire,
                               bg=BG, activebackground='grey', padx=PADX)
    button_left_mic_only = Tk.Button(master=frame_row3, text='Left mic only', command=left_mic_only,
                                     bg=BG, activebackground='grey', padx=PADX)
    button_right_mic_only = Tk.Button(master=frame_row3, text='Right mic only', command=right_mic_only,
                                      bg=BG, activebackground='grey', padx=PADX)

    ### Row 4 ####
    label_window = Tk.Label(master=frame_row4, text='Window:')
    range_window = Tk.Scale(master=frame_row4, orient=Tk.HORIZONTAL, length=120,
                            from_=0, to=len(dataset.windows)-1, command=shadow, tickinterval=1)
    if cnn_model:
        label_inference = Tk.Label(master=frame_row4, width=40, fg='DeepSkyBlue4', padx=PADX)
        label_inference.config(font=("Arial", 20))
    
    ##### Place the parts on Tk #####

    frame.pack(expand=True, fill=Tk.BOTH)

    ### Row 0: main canvas
    if args.browser:
        frame_row0a.grid(row=0, column=0)
        frame_row0b.grid(row=0, column=1)
        list_files.grid(row=0, column=0, padx=PADX_GRID)
        list_files.pack(side="left", expand=True, fill=Tk.BOTH)
        scrollbar.pack(side="right", expand=True, fill=Tk.BOTH)
    else:
        frame_row0a.pack(expand=True, fill=Tk.BOTH)
    frame_row0.pack(expand=True, fill=Tk.BOTH)
    canvas._tkcanvas.pack(expand=True, fill=Tk.BOTH)

    if args.fullscreen_mode:
        repeat_action = True
        func = globals()[args.fullscreen_mode]
        if func in (raw_wave, fft, spectrogram, mfsc, mfcc):
            func(repeatable=True)
    else:

        ### Row 1: operation ####

        frame_row1.pack(pady=PADY_GRID)

        if not cnn_model:

            if not args.oscilloscope_mode:
                # Class label entry
                label_class.grid(row=0, column=0, padx=PADX_GRID)
                entry_class_label.grid(row=0, column=1, padx=PADX_GRID)
                counter.grid(row=0, column=2, padx=PADX_GRID)

            # Waveform
            range_amplitude.grid(row=0, column=3, padx=PADX_GRID)
            button_waveform.grid(row=0, column=4, padx=PADX_GRID)

            # FFT (PSD)
            button_psd.grid(row=0, column=5, padx=PADX_GRID)

            # Linear-scale Spectrogram (PSD)
            range_spectrogram.grid(row=0, column=6, padx=PADX_GRID)
            button_spectrogram.grid(row=0, column=7, padx=PADX_GRID)

            # Welch's method
            button_welch.grid(row=0, column=8, padx=PADX_GRID)

        if not cnn_model or (cnn_model and dataset.feature == 'mfsc'):
            # Mel-scale Spectrogram (PSD)
            range_mfsc.grid(row=0, column=9, padx=PADX_GRID)
            button_mfsc.grid(row=0, column=10, padx=PADX_GRID)

        # MFCC
        if not cnn_model or (cnn_model and dataset.feature == 'mfcc'):
            range_mfcc.grid(row=0, column=11, padx=PADX_GRID)
            button_mfcc.grid(row=0, column=12, padx=PADX_GRID)

        # CMAP
        label_image.grid(row=0, column=13, padx=PADX_GRID)
        label_image.grid(row=0, column=14, padx=PADX_GRID)
        spectrum_subtraction.grid(row=0, column=15, padx=PADX_GRID)
        cmap.grid(row=0, column=16, padx=PADX_GRID)

        ### Row 2 ####

        frame_row2.pack(pady=PADY_GRID)

        # Beam forming
        label_beam_forming.grid(row=0, column=0, padx=PADX_GRID)
        label_left.grid(row=0, column=1, padx=PADX_GRID)
        range_beam_forming.grid(row=0, column=2, padx=PADX_GRID)
        label_right.grid(row=0, column=3, padx=PADX_GRID)

        # Repeat, pre_emphasis, save fig and delete
        button_repeat.grid(row=0, column=4, padx=PADX_GRID)
        button_pre_emphasis.grid(row=0, column=5, padx=PADX_GRID)
        if not cnn_model:
            if not args.oscilloscope_mode:
                button_confirm.grid(row=0, column=7, padx=PADX_GRID)
                button_save.grid(row=0, column=8, padx=PADX_GRID)
                button_remove.grid(row=0, column=9, padx=PADX_GRID)
        button_savefig.grid(row=0, column=10, padx=PADX_GRID)

        # Quit
        button_quit.grid(row=0, column=11, padx=PADX_GRID)

        ### Row 3 ####

        # DEBUG
        if args.debug:
            frame_row3.pack(pady=PADY_GRID)
            button_filterbank.grid(row=0, column=0, padx=PADX_GRID)
            button_elapsed_time.grid(row=0, column=1, padx=PADX_GRID)
            button_broadside.grid(row=0, column=2, padx=PADX_GRID)    
            button_endfire.grid(row=0, column=3, padx=PADX_GRID)            
            button_left_mic_only.grid(row=0, column=4, padx=PADX_GRID)    
            button_right_mic_only.grid(row=0, column=5, padx=PADX_GRID)    

        ### Row 4 ####
        if not args.oscilloscope_mode:
            frame_row4.pack(pady=PADY_GRID)
            label_window.grid(row=0, column=0, padx=PADX_GRID)
            range_window.grid(row=0, column=1, padx=PADX_GRID)
            if cnn_model:
                label_inference.grid(row=0, column=2, padx=PADX_GRID)
                label_inference.configure(text='...')

    ##### loop forever #####
    Tk.mainloop()
