# << Digial signal processing for oscilloscope GUI >>
#
# (1) Interface to the edge device (STM32L4 w/ my original
#     MEMS mic Arduino shield)
# (2) Plot the data with matplotlib
#
# Follow the definition in the include files below:
# https://github.com/araobp/acoustic-event-detection/tree/master/stm32/Inc
#

import serial
import pandas as pd
import numpy as np

### Constants #####

Fs = 80000000.0/128.0/32.0  # Sampling frequency
Nyq = Fs/2.0                # Nyquist frequency
NUM_FILTERS_MEL = 40        # The number of filters in the filter bank
NUM_FILTERS_SPEC = 255      # The number of filters in the filter bank
BAUD_RATE = 460800          # UART baud rate

# main.c
RAW_WAVE = b'0'
FFT = b'1'
SPECTROGRAM = b'6'
MEL_SPECTROGRAM = b'3'
MFCC = b'4'

# main.c
NUM_SAMPLES = {}            # The number of samples to receive from the device
NUM_SAMPLES[RAW_WAVE] = 512
NUM_SAMPLES[FFT] = 256
NUM_SAMPLES[SPECTROGRAM] = 255 * 200
NUM_SAMPLES[MEL_SPECTROGRAM] = 40 * 200
NUM_SAMPLES[MFCC] = 40 * 200

# Time and frequency
TIME = {}
FREQ = {}
TIME[RAW_WAVE] = np.linspace(0, NUM_SAMPLES[RAW_WAVE]/Fs*1000.0, NUM_SAMPLES[RAW_WAVE])
FREQ[FFT] = np.linspace(0, Fs/2, NUM_SAMPLES[FFT])
TIME[SPECTROGRAM] = np.linspace(0, NUM_SAMPLES[RAW_WAVE]/Fs*200.0/2, 200)
FREQ[SPECTROGRAM] = np.linspace(Nyq/(NUM_FILTERS_SPEC+1), Nyq - Nyq/(NUM_FILTERS_SPEC+1), NUM_FILTERS_SPEC)
TIME[MEL_SPECTROGRAM] = np.linspace(0, NUM_SAMPLES[RAW_WAVE]/Fs*200.0/2, 200)
FREQ[MEL_SPECTROGRAM] = np.linspace(1, NUM_FILTERS_MEL+1, NUM_FILTERS_MEL)
TIME[MFCC] = np.linspace(0, NUM_SAMPLES[RAW_WAVE]/Fs*200.0/2, 200)
FREQ[MFCC] = np.linspace(1, NUM_FILTERS_MEL, NUM_FILTERS_MEL)

###################

# Serial interface
ser = None
_port = None

def init(port):
    global _port, ser
    _port = port
    ser = serial.Serial(_port, BAUD_RATE)

def close():
    ser.close()
    
# As an application processor, send a command
# then receive and process the output.
def _serial_read(cmd, ssub=None):
    try:
        data = []
        id_ = 0
        n = 0

        ser.write(cmd)
        if cmd == RAW_WAVE:  # 16bit quantization
            rx = ser.read(NUM_SAMPLES[cmd]*2)
            rx = zip(rx[0::2], rx[1::2])
            for msb, lsb in rx:
                n += 1
                d =  int.from_bytes([msb, lsb], byteorder='big', signed=True)
                data.append((0,n,d))    
        else:  # 8bit quantization
            rx = ser.read(NUM_SAMPLES[cmd])
            for d in rx:
                n += 1
                d =  int.from_bytes([d], byteorder='big', signed=True)
                if ssub and (ssub > 0):
                    d = d - ssub
                    if d < 0:
                        d = 0.0
                data.append((0,n,d))
    except:
        print('serial connection error!')
        ser.close()

    labels = ['id', 'n', 'magnitude']
    df = pd.DataFrame(data, columns=labels)
    return df

def enable_pre_emphasis(enable):
    if enable:
        ser.write(b'P')
    else:
        ser.write(b'p')

def set_beam_forming(mode, angle):
    if mode in ('e', 'b') and angle in ('R', 'r', 'c', 'l', 'L', 'b', 'e'):
        m = mode.encode('ascii')
        ser.write(m)
        a = angle.encode('ascii')
        ser.write(a)

# Use matplotlib to plot the output from the device
def plot_aed(ax, cmd, range_=None, cmap=None, ssub=None):

    df = _serial_read(cmd, ssub)
    mag = df['magnitude']
    
    if cmd == RAW_WAVE:
        ax.set_title('Time domain')
        ax.plot(TIME[RAW_WAVE], mag)
        ax.set_xlabel('Time [msec]')
        ax.set_ylabel('Amplitude')
        ax.set_ylim([-range_, range_])

    elif cmd == FFT:
        ax.set_title('Frequency domain')
        ax.plot(FREQ[FFT], mag)
        ax.set_xlabel('Frequency [Hz]')
        ax.set_ylabel('PSD [dB]')
        ax.set_ylim([-8, 127])

    elif cmd == SPECTROGRAM:
        filtered = mag.values.reshape(200, NUM_FILTERS_SPEC)
        ax.pcolormesh(TIME[SPECTROGRAM],
                      FREQ[SPECTROGRAM][:range_],
                      filtered.T[:range_],
                      cmap=cmap)
        ax.set_title('Spectrogram (PSD in dB)')
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('Frequency (Hz)')

    elif cmd == MEL_SPECTROGRAM:
        filtered = mag.values.reshape(200, NUM_FILTERS_MEL)
        ax.pcolormesh(TIME[MEL_SPECTROGRAM],
                      FREQ[MEL_SPECTROGRAM][:range_],
                      filtered.T[:range_],
                      cmap=cmap)
        ax.set_title('Mel-scale spectrogram (PSD in dB)')
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('Mel-scale filters')

    elif cmd == MFCC:
        filtered = mag.values.reshape(200, NUM_FILTERS_MEL)
        ax.pcolormesh(TIME[MFCC],
                      FREQ[MFCC][:range_],
                      filtered.T[:range_],
                      cmap=cmap)
        ax.set_title('MFCCs')
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('MFCC')

    return df

