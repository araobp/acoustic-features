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
NUM_FILTERS = 64            # The number of filters in the filter bank
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
MFSC = b'98'
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
SHAPE[MFSC] = (200, NUM_FILTERS)
SHAPE[MFCC] = (200, NUM_FILTERS)

###################


b16_to_int = lambda msb, lsb, signed: int.from_bytes([msb, lsb], byteorder='big', signed=signed)
b8_to_int = lambda d, signed: int.from_bytes([d], byteorder='big', signed=signed)

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
            try:
                ser = self.serial_port()
                ser.write(cmd)

                if cmd == RAW_WAVE:  # 16bit quantization
                    rx = ser.read(NUM_SAMPLES[cmd]*2)
                    rx = zip(rx[0::2], rx[1::2])
                    for msb, lsb in rx:
                        d = b16_to_int(msb, lsb, True)
                        data.append(d)
                    data = np.array(data, dtype=np.int16)
                elif cmd == FILTERBANK:
                    filterbank = []
                    k_range = []
                    while True:
                        rx = ser.readline().decode('ascii').rstrip('\n,')
                        if rx == 'e':
                            break
                        temp = rx.split(',')
                        k_range.append(np.array(temp[0].split(':'), dtype=int))
                        filterbank.append(np.array(temp[1:], dtype=float))
                    #print(k_range)
                    #print(filterbank)
                    data = (k_range, filterbank)
                elif cmd == ELAPSED_TIME:
                    data = ser.readline().decode('ascii').rstrip('\n,')
                    print(data)
                elif cmd == FEATURES:
                    rx = ser.read(NUM_SAMPLES[cmd])
                    n = 0
                    half = int(NUM_SAMPLES[cmd]/2)
                    for d in rx:
                        d = b8_to_int(d, True)
                        if n < half:
                            if ssub:
                                d = d - sub if d > sub else -sub
                        n += 1
                        data.append(d)
                    data = np.array(data, dtype=np.int)
                    data = data.reshape(SHAPE[cmd])                    
                else:  # 8bit quantization
                    rx = ser.read(NUM_SAMPLES[cmd])
                    for d in rx:
                        d  = b8_to_int(d, True)
                        if ssub:
                            d = d - sub if d > sub else 0.0              
                        data.append(d)
                    data = np.array(data, dtype=np.int)
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
