import serial
import pandas as pd
import numpy as np

Fs = 80_000_000.0/128.0/32.0
Nyq = Fs/2.0
FRAME_LENGTH = 512
NUM_FILTERS = 40
NUM_FILTERS_L = 255
BAUD_RATE = 921600

PORT = 'COM15'

RAW_WAVE = b'0'
PSD = b'1'
FILTERBANK = b'2'
FILTERED_MEL = b'3'
FILTERED_LINEAR = b'6'
MFCC = b'4'

## Note: dirty but simplest way for setting attributes from a main program 
range_waveform = 2**9
range_filtered = NUM_FILTERS
range_mfcc = 13
cmap = 'hot'
####################

def serial_read(cmd):
    ser = serial.Serial(PORT, BAUD_RATE)
    data = []
    id_ = 0
    n = 0
    
    ser.write(cmd)
    while True:
        line = ser.readline().decode('ascii')
        records = line[:-3].split(',')  # exclude the last ','
        delim = line[-2]  # exclude '\n'
        for r in records:
            data.append((id_, n, int(r)))
            n += 1
        if delim == 'e':
            break
        elif delim == 'd':
            id_ += 1
            n = 0
    ser.close()

    labels = ['id', 'n', 'magnitude']
    df = pd.DataFrame(data, columns=labels)
    return df

def enable_pre_emphasis(enable):
    ser = serial.Serial(PORT, BAUD_RATE)
    if enable:
        ser.write(b'P')
    else:
        ser.write(b'p')
    ser.close()

def enable_mean_normalization(enable):
    ser = serial.Serial(PORT, BAUD_RATE)
    if enable:
        ser.write(b'M')
    else:
        ser.write(b'm')
    ser.close()

def plot_aed(ax, df, cmd):
    
    if cmd == RAW_WAVE:
        t = np.linspace(0, FRAME_LENGTH/Fs*1000.0, FRAME_LENGTH)
        ax.set_title('Time domain')
        ax.plot(t, df['magnitude'])
        ax.set_xlabel('Time [msec]')
        ax.set_ylabel('Amplitude')
        ax.set_ylim([-range_waveform, range_waveform])

    elif cmd == PSD:
        freq = np.linspace(0, Fs/2, FRAME_LENGTH/2)
        ax.set_title('Frequency domain')
        ax.plot(freq, df['magnitude'])
        ax.set_xlabel('Frequency [Hz]')
        ax.set_ylabel('PSD [dB]')
        ax.set_ylim([-40, 120])

    elif cmd == FILTERBANK:
        filterbank = df['magnitude'].values.reshape(NUM_FILTERS,int(FRAME_LENGTH/6))
        for m in range(0, NUM_FILTERS):
            ax.plot(filterbank[m])

    elif cmd == FILTERED_MEL:
        filtered = df['magnitude'].values.reshape(200, NUM_FILTERS)
        t = np.linspace(0, FRAME_LENGTH/Fs*200.0/2, 200)
        f = np.linspace(1, NUM_FILTERS+1, NUM_FILTERS)
        ax.pcolormesh(t, f[:range_filtered], filtered.T[:range_filtered], cmap=cmap)
        ax.set_title('Mel-scale spectrogram (PSD in dB)')
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('Mel-scale filters')

    elif cmd == FILTERED_LINEAR:
        filtered = df['magnitude'].values.reshape(200, NUM_FILTERS_L)
        t = np.linspace(0, FRAME_LENGTH/Fs*200.0/2, 200)
        f = np.linspace(Nyq/(NUM_FILTERS_L+1), Nyq - Nyq/(NUM_FILTERS_L+1), NUM_FILTERS_L)
        ax.pcolormesh(t, f[:range_filtered], filtered.T[:range_filtered], cmap=cmap)
        ax.set_title('Spectrogram (PSD in dB)')
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('Frequency (Hz)')

    elif cmd == MFCC:
        filtered = df['magnitude'].values.reshape(200, NUM_FILTERS)
        t = np.linspace(0, FRAME_LENGTH/Fs*200.0/2, 200)
        f = np.linspace(1, NUM_FILTERS, NUM_FILTERS)
        ax.pcolormesh(t, f[:range_mfcc], filtered.T[:range_mfcc], cmap=cmap)
        ax.set_title('MFCCs')
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('MFCC')

