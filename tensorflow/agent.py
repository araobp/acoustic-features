from keras import models
import serial
import numpy as np
import pandas as pd
import yaml
import sklearn.preprocessing as pp
import time


DATA_FOLDER = '../oscilloscope/data/data_music/'

#MODEL = './cnn_for_aed_20181108100417.h5'
MODEL = './cnn_for_aed_20181107185253.h5'

FILTERED_MEL = b'3'
PORT = 'COM15'
BAUD_RATE = 921600


def serial_read():
    ser = serial.Serial(PORT, BAUD_RATE)
    data = []
    id_ = 0
    n = 0
    
    ser.write(FILTERED_MEL)
    while True:
        line = ser.readline().decode('ascii')
        records = line[:-3].split(',')  # exclude the last ','
        delim = line[-2]  # exclude '\n'
        for r in records:
            data.append(int(r))
        if delim == 'e':
            break

    ser.close()
    data = pp.scale(np.array(data).astype(float))
    return data.reshape(200, 40, 1)
    
with open(DATA_FOLDER+'class_labels.yaml', 'r') as f:
    class_labels = yaml.load(f)

#print(class_labels)

model = models.load_model(MODEL)
model.summary()

layer_outputs = [layer.output for layer in model.layers]
activation_model = models.Model(inputs=model.input, outputs=layer_outputs)

cnt = 0
while True:
    
    time.sleep(1)
    data_a = serial_read()
    data1 = data_a[:64,:, :]
    data2 = data_a[64:128,:, :]
    data3 = data_a[128:192,:, :]
    data_b = serial_read()
    data4 = data_b[:64,:, :]
    data5 = data_b[64:128,:, :]
    data6 = data_b[128:192,:, :]
    data = np.array([data1, data2, data3, data4, data5, data6])
    
    activations = activation_model.predict(data)
    prediction_result = (activations[-1]*100).astype(int)

    p = np.sum(prediction_result, axis=0)/6.0
    max_idx = np.argmax(p)

    print()
    print('<<< ({}) this is {} ({:.1f}%) >>>'.format(cnt, class_labels[max_idx], p[max_idx]))
    for i in range(len(p)):
        print('{}: {:.1f}%'.format(class_labels[i], p[i]))
    cnt += 1
