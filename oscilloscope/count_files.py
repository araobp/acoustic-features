# Count the number of files for each class label

import glob

FOLDER = './data/'

class_labels = ['piano',
                'classical_guitar',
                'framenco_guitar',
                'tin_whistle',
                'blues_harp']

cnt = 0
for label in class_labels:
    l = glob.glob(FOLDER + '*' + label + '*.csv')
    for f in l:
        cnt += 1
    print('{}: {}'.format(label, cnt))
    cnt = 0
