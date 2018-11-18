#!/usr/bin/env python3

from keras import models
import serial
import numpy as np
import pandas as pd
import yaml
import sklearn.preprocessing as pp
import time
import sys

# MODEL = './cnn_for_aed_20181107185253.h5'
# MODEL = './cnn_for_aed_20181110221837.h5'
# MODEL = './cnn_for_aed_20181111211558.h5'
MODEL = sys.argv[1]
CLASS_FOLDER = sys.argv[2]

FILTERED_MEL = b'3'
#PORT = 'COM15'
PORT = '/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066BFF323532543457234431-if02' 
BAUD_RATE = 460800 

FRAME_LENGTH = 40 * 200


def serial_read():
    ser = serial.Serial(PORT, BAUD_RATE)
    data = []
    id_ = 0
    n = 0
    
    ser.write(FILTERED_MEL)
    rx = ser.read(FRAME_LENGTH)
    for d in rx:
        n += 1
        d = int.from_bytes([int(d)], byteorder='little', signed=True)
        data.append(d)

    ser.close()
    data = pp.scale(np.array(data).astype(float))
    return data.reshape(200, 40, 1)
    
with open(CLASS_FOLDER+'class_labels.yaml', 'r') as f:
    class_labels = yaml.load(f)

#print(class_labels)

model = models.load_model(MODEL)
model.summary()

layer_outputs = [layer.output for layer in model.layers]
activation_model = models.Model(inputs=model.input, outputs=layer_outputs)

prediction_result = np.zeros(shape=(9, len(class_labels)), dtype=float)

cnt = 0
while True:
    
    time.sleep(1)
    data_a = serial_read()
    data1 = data_a[:64,:, :]
    data2 = data_a[64:128,:, :]
    data3 = data_a[128:192,:, :]

    data = np.array([data1, data2, data3])
    
    activations = activation_model.predict(data)
    result = (activations[-1]*100)
    prediction_result[0:6] = prediction_result[3:9]
    prediction_result[6:9] = result
    p = np.sum(prediction_result, axis=0)/9.0
    max_idx = np.argmax(p)

    print()
    print('<<< ({}) this is {} ({:.1f}%) >>>'.format(cnt, class_labels[max_idx], p[max_idx]))
    for i in range(len(p)):
        print('{}: {:.1f}%'.format(class_labels[i], p[i]))
    cnt += 1
