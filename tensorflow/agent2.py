#!/usr/bin/env python3

from keras import models
import serial
import numpy as np
import pandas as pd
import yaml
import sklearn.preprocessing as pp
import time
import sys
import os

MODEL = sys.argv[1]
CLASS_FOLDER = sys.argv[2]

MFCC = b'4'
#PORT = 'COM15'
PORT = '/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066BFF323532543457234431-if02' 
BAUD_RATE = 460800 

FRAME_LENGTH = 40 * 200


def serial_read():
    ser = serial.Serial(PORT, BAUD_RATE)
    data = []
    id_ = 0
    n = 0
    
    ser.write(MFCC)
    rx = ser.read(FRAME_LENGTH)
    for d in rx:
        n += 1
        d = int.from_bytes([int(d)], byteorder='little', signed=True)
        data.append(d)

    ser.close()
    data = pp.scale(np.array(data).astype(float))
    data = data.reshape(200, 40, 1)
    return np.array([data[:96,:12,:],data[24:96+24,:12,:],data[48:96+48,:12,:],data[72:96+72,:12,:], data[96:192,:12,:]])
    
with open(CLASS_FOLDER+'class_labels.yaml', 'r') as f:
    class_labels = yaml.load(f)

#print(class_labels)

model = models.load_model(MODEL)
model.summary()

layer_outputs = [layer.output for layer in model.layers]
activation_model = models.Model(inputs=model.input, outputs=layer_outputs)

cnt = 0
while True:
    input('Press enter key for speech recognition ...')
    os.system('clear') 
    cnt = 0
    data = serial_read()

    activations = activation_model.predict(data)
    result = (activations[-1]*100)

    for p in result:
        max_idx = np.argmax(p*100)

        print('<<< ({}) this is {} ({:.1f}%) >>>'.format(cnt, class_labels[max_idx], p[max_idx]))
        cnt += 1
        for i in range(len(p)):
            print('{}: {:.1f}%'.format(class_labels[i], p[i]))
