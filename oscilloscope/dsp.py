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
import traceback
import threading

### Constants #####

Fs = 80000000.0/128.0/32.0  # Sampling frequency
Nyq = Fs/2.0                # Nyquist frequency
NUM_FILTERS = 40            # The number of filters in the filter bank
FILTER_LENGTH = 32
BAUD_RATE = 460800          # UART baud rate
NN = 512

# main.c
RAW_WAVE = b'1'
FFT = b'2'
SPECTROGRAM = b'3'
MEL_SPECTROGRAM = b'4'
MFCC = b'5'
FILTERBANK = b'6'

# main.c
NUM_SAMPLES = {}            # The number of samples to receive from the device
NUM_SAMPLES[RAW_WAVE] = 512
NUM_SAMPLES[FFT] = 256
NUM_SAMPLES[SPECTROGRAM] = int(NN/2) * 200
NUM_SAMPLES[MEL_SPECTROGRAM] = 40 * 200
NUM_SAMPLES[MFCC] = 40 * 200

# Time and frequency
TIME = {}
FREQ = {}
TIME[RAW_WAVE] = np.linspace(0, NUM_SAMPLES[RAW_WAVE]/Fs*1000.0, NUM_SAMPLES[RAW_WAVE])
FREQ[FFT] = np.linspace(0, Fs/2, NUM_SAMPLES[FFT])
TIME[SPECTROGRAM] = np.linspace(0, NUM_SAMPLES[RAW_WAVE]/Fs*200.0/2, 200)
FREQ[SPECTROGRAM] = np.linspace(0, Nyq, int(NN/2))
TIME[MEL_SPECTROGRAM] = np.linspace(0, NUM_SAMPLES[RAW_WAVE]/Fs*200.0/2, 200)
FREQ[MEL_SPECTROGRAM] = np.linspace(1, NUM_FILTERS+1, NUM_FILTERS)
TIME[MFCC] = np.linspace(0, NUM_SAMPLES[RAW_WAVE]/Fs*200.0/2, 200)
FREQ[MFCC] = np.linspace(1, NUM_FILTERS, NUM_FILTERS)

# Filter banks
def hz2mel(hz):
  return 2595.0 * np.log10(hz/700.0 + 1.0);

def mel2hz(mel):
  return 700.0 * (10.0**(mel/2595.0) - 1.0);

def n2hz(n):
  return float(n)/NN * nyq_fs

hz_freqs = np.zeros(NUM_FILTERS+2)
hz_freqs_n = np.zeros(NUM_FILTERS+2, dtype=int)
mel_delta = hz2mel(Nyq)/(NUM_FILTERS+2)

for m in range(0, NUM_FILTERS+2):
    hz_freqs[m] = mel2hz(mel_delta * m)
    hz_freqs_n[m] = (int)(hz_freqs[m] / Nyq * NN / 2)

###################

# GUI class

class GUI:
    
    def __init__(self, port):
        # Serial interface
        self.port = port
        self.lock = threading.Lock()

    # As an application processor, send a command
    # then receive and process the output.
    def _serial_read(self, cmd, ssub=None):

        data = []
        with self.lock:
            n = 0
            try:
                ser = serial.Serial(self.port, BAUD_RATE, timeout=3, inter_byte_timeout=3)
                ser.write(cmd)
                if cmd == RAW_WAVE:  # 16bit quantization
                    rx = ser.read(NUM_SAMPLES[cmd]*2)
                    rx = zip(rx[0::2], rx[1::2])
                    for msb, lsb in rx:
                        n += 1
                        d =  int.from_bytes([msb, lsb], byteorder='big', signed=True)
                        data.append(d)
                    data = np.array(data)
                elif cmd == FILTERBANK:
                    filterbank = []
                    while True:
                        rx = ser.readline().decode('ascii').rstrip('\n,')
                        if rx == 'e':
                            break
                        temp = rx.split(',')
                        # print(temp)
                        filterbank.extend(temp)
                    data = np.array(filterbank, dtype=float)
                else:  # 8bit quantization
                    rx = ser.read(NUM_SAMPLES[cmd])
                    for d in rx:
                        n += 1
                        d =  int.from_bytes([d], byteorder='big', signed=True)
                        if ssub and (ssub > 0):
                            d = d - ssub
                            if d < 0:
                                d = 0.0
                        data.append(d)
                    data = np.array(data)
                ser.close()
            except:
                print('*** serial timeout!')
                traceback.print_exc()

        return data

    def enable_pre_emphasis(self, enable):
        ser = serial.Serial(self.port, BAUD_RATE, timeout=3)
        if enable:
            ser.write(b'P')
        else:
            ser.write(b'p')
        ser.close()
        
    def set_beam_forming(self, mode, angle):
        if mode in ('e', 'b') and angle in ('R', 'r', 'c', 'l', 'L', 'b', 'e'):
            ser = serial.Serial(self.port, BAUD_RATE, timeout=3)
            ser.write(mode.encode('ascii'))
            ser.write(angle.encode('ascii'))
            ser.close()

    # Use matplotlib to plot the output from the device
    def plot_aed(self, ax, cmd, range_=None, cmap=None, ssub=None):

        mag = self._serial_read(cmd, ssub)
        ax.clear()
        
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
            filtered = mag.reshape(200, int(NN/2))
            ax.pcolormesh(TIME[SPECTROGRAM],
                          FREQ[SPECTROGRAM][:range_],
                          filtered.T[:range_],
                          cmap=cmap)
            ax.set_title('Spectrogram (PSD in dB)')
            ax.set_xlabel('Time [sec]')
            ax.set_ylabel('Frequency (Hz)')

        elif cmd == MEL_SPECTROGRAM:
            filtered = mag.reshape(200, NUM_FILTERS)
            ax.pcolormesh(TIME[MEL_SPECTROGRAM],
                          FREQ[MEL_SPECTROGRAM][:range_],
                          filtered.T[:range_],
                          cmap=cmap)
            ax.set_title('Mel-scale spectrogram (PSD in dB)')
            ax.set_xlabel('Time [sec]')
            ax.set_ylabel('Mel-scale filters')

        elif cmd == MFCC:
            filtered = mag.reshape(200, NUM_FILTERS)
            ax.pcolormesh(TIME[MFCC],
                          FREQ[MFCC][:range_],
                          filtered.T[:range_],
                          cmap=cmap)
            ax.set_title('MFCCs')
            ax.set_xlabel('Time [sec]')
            ax.set_ylabel('MFCC')     

        elif cmd == FILTERBANK: 
            data = mag.reshape(NUM_FILTERS+2, FILTER_LENGTH)
            for m in range(1, NUM_FILTERS+1):
                num_axis = hz_freqs_n[m]+FILTER_LENGTH
                mel = np.zeros(num_axis)
                mel[hz_freqs_n[m]:hz_freqs_n[m]+FILTER_LENGTH] = data[m]
                ax.plot(mel)
                
            ax.set_title('Mel filter bank')
            ax.set_xlabel('n')
            ax.set_ylabel('Magnitude')

        return mag
