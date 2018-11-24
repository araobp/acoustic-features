import serial
import pandas as pd
import numpy as np

Fs = 80000000.0/128.0/32.0
Nyq = Fs/2.0
FRAME_LENGTH = {}
NUM_FILTERS = 40
NUM_FILTERS_L = 255
BAUD_RATE = 460800

_port = None

# dsp.h
RAW_WAVE = b'0'
FFT = b'1'
SPECTROGRAM = b'6'
MEL_SPECTROGRAM = b'3'
MFCC = b'4'

# main.c
FRAME_LENGTH[RAW_WAVE] = 512
FRAME_LENGTH[FFT] = 256
FRAME_LENGTH[SPECTROGRAM] = 255 * 200
FRAME_LENGTH[MEL_SPECTROGRAM] = 40 * 200
FRAME_LENGTH[MFCC] = 40 * 200

def init(port):
    global _port
    _port = port

# As an application processor, send a command
# then receive and process the output.
def serial_read(cmd, ssub=None):
    ser = serial.Serial(_port, BAUD_RATE)
    data = []
    id_ = 0
    n = 0

    ser.write(cmd)
    if cmd == RAW_WAVE:  # 16bit quantization
        rx = ser.read(FRAME_LENGTH[cmd]*2)
        rx = zip(rx[0::2], rx[1::2])
        for msb, lsb in rx:
            n += 1
            d =  int.from_bytes([msb, lsb], byteorder='big', signed=True)
            data.append((0,n,d))    
    else:  # 8bit quantization
        rx = ser.read(FRAME_LENGTH[cmd])
        for d in rx:
            n += 1
            d =  int.from_bytes([d], byteorder='big', signed=True)
            if ssub and (ssub > 0):
                d = d - ssub
                if d < 0:
                    d = 0.0
            data.append((0,n,d))
    ser.close()

    labels = ['id', 'n', 'magnitude']
    df = pd.DataFrame(data, columns=labels)
    return df

def enable_pre_emphasis(enable):
    ser = serial.Serial(_port, BAUD_RATE)
    if enable:
        ser.write(b'P')
    else:
        ser.write(b'p')
    ser.close()

def set_beam_forming(mode, angle):
    if mode in ('e', 'b') and angle in ('R', 'r', 'c', 'l', 'L', 'b', 'e'):
        ser = serial.Serial(_port, BAUD_RATE)
        m = mode.encode('ascii')
        ser.write(m)
        a = angle.encode('ascii')
        ser.write(a)
        ser.close()    

# Use matplotlib to plot the output from the device
def plot_aed(ax, df, cmd, range_=None, cmap=None):
    
    if cmd == RAW_WAVE:
        t = np.linspace(0, FRAME_LENGTH[RAW_WAVE]/Fs*1000.0, FRAME_LENGTH[RAW_WAVE])
        ax.set_title('Time domain')
        ax.plot(t, df['magnitude'])
        ax.set_xlabel('Time [msec]')
        ax.set_ylabel('Amplitude')
        ax.set_ylim([-range_, range_])

    elif cmd == FFT:
        freq = np.linspace(0, Fs/2, FRAME_LENGTH[FFT])
        ax.set_title('Frequency domain')
        ax.plot(freq, df['magnitude'])
        ax.set_xlabel('Frequency [Hz]')
        ax.set_ylabel('PSD [dB]')
        ax.set_ylim([-8, 127])

    elif cmd == SPECTROGRAM:
        filtered = df['magnitude'].values.reshape(200, NUM_FILTERS_L)
        t = np.linspace(0, FRAME_LENGTH[RAW_WAVE]/Fs*200.0/2, 200)
        f = np.linspace(Nyq/(NUM_FILTERS_L+1), Nyq - Nyq/(NUM_FILTERS_L+1), NUM_FILTERS_L)
        ax.pcolormesh(t, f[:range_], filtered.T[:range_], cmap=cmap)
        ax.set_title('Spectrogram (PSD in dB)')
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('Frequency (Hz)')

    elif cmd == MEL_SPECTROGRAM:
        filtered = df['magnitude'].values.reshape(200, NUM_FILTERS)
        t = np.linspace(0, FRAME_LENGTH[RAW_WAVE]/Fs*200.0/2, 200)
        f = np.linspace(1, NUM_FILTERS+1, NUM_FILTERS)
        ax.pcolormesh(t, f[:range_], filtered.T[:range_], cmap=cmap)
        ax.set_title('Mel-scale spectrogram (PSD in dB)')
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('Mel-scale filters')

    elif cmd == MFCC:
        filtered = df['magnitude'].values.reshape(200, NUM_FILTERS)
        t = np.linspace(0, FRAME_LENGTH[RAW_WAVE]/Fs*200.0/2, 200)
        f = np.linspace(1, NUM_FILTERS, NUM_FILTERS)
        ax.pcolormesh(t, f[:range_], filtered.T[:range_], cmap=cmap)
        ax.set_title('MFCCs')
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('MFCC')

