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

I split each 40 mel-filters x 200 strides data into three 40 x 100 data: array of [0:8000]
=> Arrays of [0:4000], [2000:6000] and [4000:].

Training data set: 48 mel-scale spectrograms (40 filters x 100 strides) for each class
Test data set: 24 mel-scale spectrograms (40 filters x 100 strides) for each class

In -> Conv1 -cutoff-> Pool1 -> Conv2 -cutoff-> Pool2 -> Fully conncted (three hidden layers) -dropout-> Softmax
      128 filters      1/2     256 filters  1/2         4096/ReLu x 4096/ReLu x 4096/tanh
40 x 100             20 x 50              10 x 25
```
