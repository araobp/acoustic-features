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
        self.samples = dataset.samples
        self.lock = threading.Lock()
        self.active = False
        if self.port:
            try:
                ser = serial.Serial(self.port, BAUD_RATE)
                ser.close()
                self.active = True
            except:
                print('*** Cannot open {}!'.format(port))

        # main.c
        self.num_samples = {}            # The number of samples to receive from the device
        self.num_samples[RAW_WAVE] = NN
        self.num_samples[FFT] = int(NN/2)
        self.num_samples[SPECTROGRAM] = int(NN/2) * self.samples
        self.num_samples[FEATURES] = self.filters * self.samples * 2

        # Shapes
        self.shape = {}
        self.shape[RAW_WAVE] = None
        self.shape[FFT] = None
        self.shape[SPECTROGRAM] = (self.samples, int(NN/2))
        self.shape[FEATURES] = (self.samples * 2, self.filters)
        self.shape[MFSC] = (self.samples, self.filters)
        self.shape[MFCC] = (self.samples, self.filters)

    def is_active(self):
        return self.active

    def serial_port(self):
        return serial.Serial(self.port, BAUD_RATE, timeout=3)

    def read(self, cmd):
        '''
        As an application processor, send a command
        then receive and process the output.
        '''        
        data = []
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

    def enable_pre_emphasis(self, enable):
        '''
        Enable/disable pre-emphasis.
        '''
        ser = self.serial_port()
        if enable:
            ser.write(ENABLE_PRE_EMPHASIS)
        else:
            ser.write(DISABLE_PRE_EMPHASIS)
        ser.close()

    def set_beam_forming(self, mode, angle):
        '''
        Enable/disable beam forming
        '''
        ser = self.serial_port()
        ser.write(mode)
        ser.write(angle.encode('ascii'))
        ser.close()

    def left_mic_only(self):
        '''
        Left mic only
        '''
        ser = self.serial_port()
        ser.write(LEFT_MIC_ONLY)
        ser.close()

    def right_mic_only(self):
        '''
        Right mic only
        '''
        ser = self.serial_port()
        ser.write(RIGHT_MIC_ONLY)
        ser.close()
