# Acoustic Event Detection (AED) with TensorFlow

In development.

## Motivation

I want to develop the cheapest (and low-power-consumption) edge device of ML (for [VGGish](https://github.com/tensorflow/models/tree/master/research/audioset) and so on) with a MEMS mic, so I use ARM Cortex-M4L DSP to calculate MFCCs in realtime, and to transfer Mel-scale spectrogram or MFCCs to an IoT cloud. It is a kind of CODEC for ML, since it uses FFT and DCT via a filter bank for compressing data. In future, I will use a ML processor or FPGA for NN deployment.

## IoT network

```
Sound/voice ))) [MEMS mic]-[MFCC streamer(STM32L4)]--Bluetooth/LPWA/CAN---+
                                                                          |
Sound/voice ))) [MEMS mic]-[MFCC streamer(STM32L4)]--Bluetooth/LPWA/CAN---+--[gateway]--> IoT cloud
                                                                          |
Sound/voice ))) [MEMS mic]-[MFCC streamer(STM32L4)]--Bluetooth/LPWA/CAN---+
                                  |
                              USB serial
                                  |
                           [Oscilloscope GUI]
```

## Sampling frequency

- The highest frequency on a piano is 4186Hz, but it generate overtones: ~10kHz.
- Human voice also generates overtones: ~ 10kHz.

So samplig frequency of MFCC streamer should be around 20kHz: 20kHz/2 = 10kHz.

## DFSDM settings

- System clock: 80MHz
- Clock divider: 128
- FOSR/decimation: 32
- sinc filter: sinc3
- Sampling frequency: 80_000_000/128/32 = 19.5kHz

## Frame/stride/overlap

- number of samples per frame: 512
- length: 512/19.5kHz = 26.3msec
- stride: 13.2msec
- overlap: 50%(13.2msec)

```
26.3msec         stride
[b0|a1]            1a --> 12 MFCCs
   [a1|b1]         1b --> 12 MFCCs
      [b1|a2]      2a --> 12 MFCCs
         [a2|b2]   2b --> 12 MFCCs
            :
```
## Filter banks

Mel-scale spectrogram is used for training CNN

- Mel-scale: 40 filters (512 samples divided by (40 + 1))
- Linear-scale: 255 filters (512 samples divide by (255 + 2))

## Processing time (actual measurement)

In case of 1024 samples per frame:
- fir (cfft/mult/cifft/etc * 2 times): 17msec
- log10: 54msec
- log10 fast approximation: 1msec
- atan2: 53msec

Note: log10(x) = log10(2) * log2(x)

Reference: https://community.arm.com/tools/f/discussions/4292/cmsis-dsp-new-functionality-proposal

## log10 processing time issue

log10 of math.h is too slow for audio signal processing, but CMSIS DSP does not support log10. I decided to adopt [log10 approximation](./ipynb/log10%20fast%20approximation.ipynb).

## Command over UART (USB-serial)

UART baudrate: 921600bps

```

        Sequence over UART(USB-serial)

    ARM Cortex-M4L                    PC
           |                          |
           |<-------- cmd ------------|
           |                          |
           |------ data output ------>|
           |                          |

```

|cmd|description     | output size             | purpose               |
|---|----------------|-------------------------|-----------------------|
|0  | RAW_WAVE       | N x 1                   | Input to oscilloscope |
|1  | PSD            | N/2 x 1                 | Input to ML           |
|2  | FILTERBANK     | N/6 x NUM_FILTERS       | (for testing)         |
|3  | FILTERED_MEL   | NUM_FILTERS x 200       | Input to ML           |
|4  | MFCC           | NUM_FILTERS x 200       | Input to ML           |
|5  | MFCC_STREAMING | NUM_FILTERS x 07fffffff | (for testing)         |
|6  | FILTERED_LINEAR| NUM_FILTERS x 200       | Input to ML           |

## Oscilloscope GUI

I use Tkinter with matplotlib to draw graph of waveform, FFT, PSD, MFCCs etc.

![](./oscilloscope/screenshots/waveform.jpg)

![](./oscilloscope/screenshots/fft(psd).jpg)

![](./oscilloscope/screenshots/spectrogram(psd).jpg)

- [Oscilloscope GUI implementation on matplotlib/Tkinter](./oscilloscope)
- [Wave form and PSD of some music](./oscilloscope/images)

### Some interesting findings

- [Bulerias played by a famous framenco guitarist is ultra fast!](./oscilloscope/images/framenco_guitar_bulerias_mel_scale.png)
- [Hevy metal is like white noise of higher amplitude](./oscilloscope/images/hevy_metal_mel_scale.png)

## CNN test on TensorFlow

### Preliminary test (Oct 28, 2018)

I tested the following setup on Google's Colab with GPU acceleration:

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

Due to the limited amount of GPU resource, I could not test any CNN with a larger scale than the above.

The accuracy rate is around 80% ~ 90%. It is not so bad, since I have not made any optimization for its input data...

### Second test (Oct 30, 2018)

I retried the CNN model with 63 filters in the filter bank. The result is worse than the test on Oct 28:
- the CNN model above is still the best one I have ever tried (I have also tried other models).
- the test with 40 filters showed a better result that the test with 63 filters today.

### Third test (Oct 31, 2018)

- I added ReLu to cutoff negative output from the convolution layers.
- I also added dropout layer to avoid overfitting.

The result is still the same: the 40-filter data set beats the 63-filter data set.

## TODO

- Correlation filters for detecting music instruments: bandpass filter for extracting A4(440Hz) or A5(880Hz) from sound of various music instruments.
