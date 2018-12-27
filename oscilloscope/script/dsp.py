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
BAUD_RATE = 460800          # UART baud rate
NN = 512                    # The number of samples per frame

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

###################

b16_to_int = lambda msb, lsb, signed: int.from_bytes([msb, lsb], byteorder='big', signed=signed)
b8_to_int = lambda d, signed: int.from_bytes([d], byteorder='big', signed=signed)

# Interface class
class Interface:
    
    def __init__(self, port, dataset):
        # Serial interface
        self.port = port
        self.filters = dataset.filters
        self.length = dataset.length
        self.lock = threading.Lock()
        try:
            ser = serial.Serial(self.port, BAUD_RATE)
            ser.close()
        except:
            print('*** Cannot open {}!'.format(port))
            
        # main.c
        self.num_samples = {}            # The number of samples to receive from the device
        self.num_samples[RAW_WAVE] = NN
        self.num_samples[FFT] = int(NN/2)
        self.num_samples[SPECTROGRAM] = int(NN/2) * self.length
        self.num_samples[FEATURES] = self.filters * self.length * 2

        # Shapes
        self.shape = {}
        self.shape[RAW_WAVE] = None
        self.shape[FFT] = None
        self.shape[SPECTROGRAM] = (self.length, int(NN/2))
        self.shape[FEATURES] = (self.length * 2, self.filters)
        self.shape[MFSC] = (self.length, self.filters)
        self.shape[MFCC] = (self.length, self.filters)

    def serial_port(self):
        return serial.Serial(self.port, BAUD_RATE, timeout=3)

    # As an application processor, send a command
    # then receive and process the output.
    def read(self, cmd):
        
        data = []
        with self.lock:
            try:
                ser = self.serial_port()
                ser.write(cmd)

                if cmd == RAW_WAVE:  # 16bit quantization
                    rx = ser.read(self.num_samples[cmd]*2)
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
                    data = (k_range, filterbank)
                elif cmd == ELAPSED_TIME:
                    data = ser.readline().decode('ascii').rstrip('\n,')
                    print(data)
                elif cmd == FEATURES:
                    rx = ser.read(self.num_samples[cmd])
                    n = 0
                    half = int(self.num_samples[cmd]/2)
                    for d in rx:
                        d = b8_to_int(d, True)
                        data.append(d)
                    data = np.array(data, dtype=np.int)
                    data = data.reshape(self.shape[cmd])                    
                else:  # 8bit quantization
                    rx = ser.read(self.num_samples[cmd])
                    for d in rx:
                        d  = b8_to_int(d, True)
                        data.append(d)
                    data = np.array(data, dtype=np.int)
                    if self.shape[cmd]:
                        data = data.reshape(self.shape[cmd])
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
