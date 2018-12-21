# Generate dataset for Keras/TensorFlow

import yaml
import numpy as np
import sklearn.preprocessing as pp
import random
import os
import time
import glob
from keras.utils import to_categorical

class DataSet:
    '''
     - /dataset_folder --+-- /data/*.csv
                         |
                         +-- /dataset.yaml
                         |
                         +-- /class_labels.yaml
                         |
                         +-- /*.h5
    '''

    def __init__(self, dataset_folder):

        self.dataset_folder = dataset_folder    
        with open(dataset_folder + '/dataset.yaml') as f:
            attr = yaml.load(f)
        self.filters = attr['filters']
        self.files = attr['files']
        self.length = attr['length']
        self.training_files = attr['training_files']
        self.test_files = self.files - self.training_files
        self.feature = attr['feature']
        self.stride = attr['stride']
        self.cutoff = attr['cutoff']
        self.window_pos = attr['window_pos']
        self.model = attr['model']
        
        if not self.cutoff:
            self.cutoff = self.filters
        if self.window_pos is None:
            self.window_pos = -1

        self.class_labels = None
        self.train_data = None
        self.train_labels = None
        self.test_data = None
        self.test_labels = None
        
        if self.feature == 'mfcc':
            self.shape = (self.length, self.cutoff-1)  # DC removed
        else:
            self.shape = (self.length, self.cutoff)

    def generate_windows(self):
        '''
        Generate windows
        '''
        windows = []
        a, b, i = 0, 0, 0
        while True:
            a, b = self.stride*i, self.stride*i+self.length
            if b > 200:
                break
            windows.append([a, b, self.cutoff])
            i += 1
        return (windows, self.window_pos)   # Backward compatibility: window_pos is to be removed in future
        
    def generate(self):
        '''
        Generate training data set and test data set for Keras/TensorFlow
        '''

        data_files = glob.glob(self.dataset_folder+'/data/*{}*.csv'.format(self.feature))
        class_labels = []

        for file in data_files:
            label = file.split('-')[0].replace('\\', '/').split('/')[-1]
            if label not in class_labels:
                class_labels.append(label)

        data_set = {}
        class_number = 0

        for label in class_labels:
            files = glob.glob(self.dataset_folder+'/data/{}-*{}*.csv'.format(label, self.feature))
            random.shuffle(files)
            data_set[label] = (files[:self.training_files], files[self.training_files:self.files], class_number)
            class_number += 1

        training_set = []
        test_set = []
        
        windows, window_pos = self.generate_windows()

        if window_pos >= 0:
            windows = [windows[window_pos]]
            
        for k, v in data_set.items():
            files = v[0]
            class_number = v[2]
            for file in files:
                params = file.split('-')
                if len(params) > 3:
                    pos = file.split('-')[2]
                else:  # Backward compatibility (to be removed in future)
                    pos = None
                with open(file) as f:
                    data = np.array(f.read().split(',')).astype(float)
                    if pos:
                        w = windows[pos]
                        img = pp.scale(data[w[0]*self.filters:w[1]*self.filters])
                        training_set.append((img, class_number))                        
                    else:
                        for w in windows:
                            img = pp.scale(data[w[0]*self.filters:w[1]*self.filters])
                            training_set.append((img, class_number))
            files = v[1]
            for file in files:
                params = file.split('-')
                if len(params) > 3:
                    pos = int(file.split('-')[2])
                else:  # Backward compatibility (to be removed in future)
                    pos = None
                with open(file) as f:
                    data = np.array(f.read().split(',')).astype(float)
                    if pos:
                        w = windows[pos]
                        img = pp.scale(data[w[0]*self.filters:w[1]*self.filters])
                        training_set.append((img, class_number))                        
                    else:
                        for w in windows:
                            img = pp.scale(data[w[0]*self.filters:w[1]*self.filters])
                            test_set.append((img, class_number))

        random.shuffle(training_set)
        random.shuffle(test_set)

        self.class_labels = [None for _ in range(len(data_set))]

        # Class number and class labels
        for k,v in data_set.items():
            self.class_labels[v[2]] = k
            
        with open(self.dataset_folder+'/class_labels.yaml', 'w') as f:
            yaml.dump(self.class_labels, f)

        train_data, train_labels = [], []
        test_data, test_labels = [], []

        for img, label in training_set:
            train_data.append(img)
            train_labels.append(label)

        for img, label in test_set:
            test_data.append(img)
            test_labels.append(label)

        train_data = np.array(train_data, dtype='float32').reshape((self.training_files*len(class_labels)*len(windows), self.length, self.filters, 1))
        if self.feature == 'mfcc':
            train_data = train_data[:,:,1:self.cutoff,:]  # Remove DC
        else:
            train_data = train_data[:,:,0:self.cutoff,:]            
        train_labels = np.array(train_labels, dtype='uint8')
        test_data = np.array(test_data, dtype='float32').reshape((self.test_files*len(class_labels)*len(windows), self.length, self.filters, 1))
        if self.feature == 'mfcc':
            test_data = test_data[:,:,1:self.cutoff,:]  # Remove DC
        else:
            test_data = test_data[:,:,0:self.cutoff,:]            
        test_lables = np.array(test_labels, dtype='uint8')

        train_labels=to_categorical(train_labels)
        test_labels=to_categorical(test_labels)

        self.train_data = train_data
        self.train_labels = train_labels
        self.test_data = test_data
        self.test_labels = test_labels
        
        return (train_data, train_labels, test_data, test_labels)

    def get_shape(self):
        if self.feature == 'mfcc':
            return (self.length, self.cutoff-1)  # DC removed
        else:
            return (self.length, self.cutoff)
 