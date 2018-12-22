# << Digial signal processing for oscilloscope GUI >>
#
# Interface to the edge device (STM32L4 w/ my original MEMS mic Arduino shield)
#
# Follow the definition in the include files below:
# https://github.com/araobp/acoustic-event-detection/tree/master/stm32/Inc

import serial
import pandas as pd
import numpy as np
import traceback
import threading

### Constants #####

Fs = 80000000.0/128.0/32.0  # Sampling frequency
Nyq = Fs/2.0                # Nyquist frequency
NUM_FILTERS = 40            # The number of filters in the filter bank
BAUD_RATE = 460800          # UART baud rate
NN = 512                    # The number of samples per frame

FILTER_LENGTH = 32          # Filter length of each filter in the filter bank

# Command
RAW_WAVE = b'1'
FFT = b'2'
SPECTROGRAM = b'3'
FEATURES = b'4'
FILTERBANK = b'f'
ELAPSED_TIME = b't'
ENABLE_PRE_EMPHASIS = b'P'
DISABLE_PRE_EMPHASIS = b'p'
LEFT_MIC_ONLY = b'['
RIGHT_MIC_ONLY = b']'
BROADSIDE = b'b'
ENDFIRE = b'e'

# Features
MEL_SPECTROGRAM = b'98'
MFCC = b'99'

# main.c
NUM_SAMPLES = {}            # The number of samples to receive from the device
NUM_SAMPLES[RAW_WAVE] = 512
NUM_SAMPLES[FFT] = 256
NUM_SAMPLES[SPECTROGRAM] = int(NN/2) * 200
NUM_SAMPLES[FEATURES] = NUM_FILTERS * 200 * 2

# Shapes
SHAPE = {}
SHAPE[RAW_WAVE] = None
SHAPE[FFT] = None
SHAPE[SPECTROGRAM] = (200, int(NN/2))
SHAPE[FEATURES] = (400, NUM_FILTERS)
SHAPE[MEL_SPECTROGRAM] = (200, NUM_FILTERS)
SHAPE[MFCC] = (200, NUM_FILTERS)

###################

# Interface class
class Interface:
    
    def __init__(self, port):
        # Serial interface
        self.port = port
        self.lock = threading.Lock()
        try:
            ser = serial.Serial(self.port, BAUD_RATE)
            ser.close()
        except:
            print('*** Cannot open {}!'.format(port))
   
    def serial_port(self):
        return serial.Serial(self.port, BAUD_RATE, timeout=3)

    # As an application processor, send a command
    # then receive and process the output.
    def read(self, cmd, ssub=None):
        
        data = []
        with self.lock:
            n = 0
            try:
                ser = self.serial_port()
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
                    if SHAPE[cmd]:
                        data = data.reshape(SHAPE[cmd])
                ser.close()
            except:
                print('*** serial timeout!')
                #traceback.print_exc()

        return data

    # Enable/disable pre-emphasis
    def enable_pre_emphasis(self, enable):
        ser = self.serial_port()
        if enable:
            ser.write(ENABLE_PRE_EMPHASIS)
        else:
            ser.write(DISABLE_PRE_EMPHASIS)
        ser.close()

    # Enable/disable beam forming
    def set_beam_forming(self, mode, angle):
        ser = self.serial_port()
        ser.write(mode)
        ser.write(angle.encode('ascii'))
        ser.close()

    # Left mic only
    def left_mic_only(self):
        ser = self.serial_port()
        ser.write(LEFT_MIC_ONLY)
        ser.close()

    # Right mic only
    def right_mic_only(self):
        ser = self.serial_port()
        ser.write(RIGHT_MIC_ONLY)
        ser.close()
