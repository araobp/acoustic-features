# CNN on TensorFlow

The files in this folder are copies of ipynb files on Colab.

## Model

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

In -> Conv1 --> Pool1 -> Conv2 --> Pool2 -> Conv3 --> Pool3 -> Fully conncted (three hidden layers) -dropout-> Softmax
     16 filters   1/2   32 filters   1/2   64 filters   1/2     4096/ReLu x 4096/ReLu x 4096/tanh
40 x 64         20 x 32            10 x 14             5 x 7
```
