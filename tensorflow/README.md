# CNN on TensorFlow

The files in this folder are copies of ipynb files on Colab.

## Class labels and data set

```
Classes:
- piano music
- classial guitar music
- framenco guitar music
- blues harp music
- tin whistle music

Conditions:
- Pre emphasis enabled on the raw data.

I split each 40 mel-filters x 200 strdes data into three three 40 x 64 data.

Training data set: 48 mel-scale spectrograms (40 filters x 64 strides) for each class
Test data set: 24 mel-scale spectrograms (40 filters x 64 strides) for each class
```

## CNN model (on Keras/TensorFlow)

```
Using TensorFlow backend.
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
conv2d_1 (Conv2D)            (None, 64, 40, 64)        640       
_________________________________________________________________
max_pooling2d_1 (MaxPooling2 (None, 32, 20, 64)        0         
_________________________________________________________________
conv2d_2 (Conv2D)            (None, 32, 20, 128)       73856     
_________________________________________________________________
max_pooling2d_2 (MaxPooling2 (None, 16, 10, 128)       0         
_________________________________________________________________
conv2d_3 (Conv2D)            (None, 16, 10, 256)       295168    
_________________________________________________________________
max_pooling2d_3 (MaxPooling2 (None, 8, 5, 256)         0         
_________________________________________________________________
flatten_1 (Flatten)          (None, 10240)             0         
_________________________________________________________________
dense_1 (Dense)              (None, 256)               2621696   
_________________________________________________________________
dense_2 (Dense)              (None, 128)               32896     
_________________________________________________________________
dense_3 (Dense)              (None, 5)                 645       
=================================================================
Total params: 3,024,901
Trainable params: 3,024,901
Non-trainable params: 0
_________________________________________________________________
```
