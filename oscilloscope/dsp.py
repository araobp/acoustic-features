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
import utils

### Constants #####

Fs = 80000000.0/128.0/32.0  # Sampling frequency
Nyq = Fs/2.0                # Nyquist frequency
NUM_FILTERS = 40            # The number of filters in the filter bank
BAUD_RATE = 460800          # UART baud rate
NN = 512                    # The number of samples per frame

FILTER_LENGTH = 32          # Filter length of each filter in the filter bank

# main.c
RAW_WAVE = b'1'
FFT = b'2'
SPECTROGRAM = b'3'
MEL_SPECTROGRAM = b'4'
MFCC = b'5'

# main.h
FILTERBANK = b'f'
ELAPSED_TIME = b't'

ENABLE_PRE_EMPHASIS = b'P'
DISABLE_PRE_EMPHASIS = b'p'

LEFT_MIC_ONLY = b'['
RIGHT_MIC_ONLY = b']'
BROADSIDE = b'b'
ENDFIRE = b'e'

# main.c
NUM_SAMPLES = {}            # The number of samples to receive from the device
NUM_SAMPLES[RAW_WAVE] = 512
NUM_SAMPLES[FFT] = 256
NUM_SAMPLES[SPECTROGRAM] = int(NN/2) * 200
NUM_SAMPLES[MEL_SPECTROGRAM] = 40 * 200
NUM_SAMPLES[MFCC] = 40 * 200

# Time axis and frequency axis
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

# Empty array
EMPTY = np.array([])

# Convert frequency to Mel
def hz2mel(hz):
  return 2595.0 * np.log10(hz/700.0 + 1.0);

# Convert Mel to frequency
def mel2hz(mel):
  return 700.0 * (10.0**(mel/2595.0) - 1.0);

# Convert n to frequency
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
                    data = np.array(data, dtype=np.int16)
                elif cmd == FILTERBANK:
                    filterbank = []
                    while True:
                        rx = ser.readline().decode('ascii').rstrip('\n,')
                        if rx == 'e':
                            break
                        temp = rx.split(',')
                        print(temp)
                        filterbank.extend(temp)
                    data = np.array(filterbank, dtype=float)
                elif cmd == ELAPSED_TIME:
                    data = ser.readline().decode('ascii').rstrip('\n,')
                    print(data)
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
                    data = np.array(data, dtype=np.int8)
                ser.close()
            except:
                print('*** serial timeout!')
                traceback.print_exc()

        return data

    # Enable/disable pre-emphasis
    def enable_pre_emphasis(self, enable):
        ser = serial.Serial(self.port, BAUD_RATE, timeout=3)
        if enable:
            ser.write(ENABLE_PRE_EMPHASIS)
        else:
            ser.write(DISABLE_PRE_EMPHASIS)
        ser.close()

    # Enable/disable beam forming
    def set_beam_forming(self, mode, angle):
        ser = serial.Serial(self.port, BAUD_RATE, timeout=3)
        ser.write(mode)
        ser.write(angle.encode('ascii'))
        ser.close()

    # Left mic only
    def left_mic_only(self):
        ser = serial.Serial(self.port, BAUD_RATE, timeout=3)
        ser.write(LEFT_MIC_ONLY)
        ser.close()

    # Right mic only
    def right_mic_only(self):
        ser = serial.Serial(self.port, BAUD_RATE, timeout=3)
        ser.write(RIGHT_MIC_ONLY)
        ser.close()

    # Use matplotlib to plot the output from the device
    def plot_aed(self, ax, cmd, range_=None,
                 cmap=None, ssub=None,
                 window=None, mag=EMPTY, shadow_sub=0):

        if mag is EMPTY:
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
            if window:
                filtered = utils.shadow(filtered, window, shadow_sub=10)
            ax.pcolormesh(TIME[MEL_SPECTROGRAM],
                          FREQ[MEL_SPECTROGRAM][:range_],
                          filtered.T[:range_],
                          cmap=cmap)
            ax.set_title('Mel-scale spectrogram (PSD in dB)')
            ax.set_xlabel('Time [sec]')
            ax.set_ylabel('Mel-scale filters')

        elif cmd == MFCC:
            filtered = mag.reshape(200, NUM_FILTERS)
            if window:
                filtered = utils.shadow(filtered, window, shadow_sub=10)
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
