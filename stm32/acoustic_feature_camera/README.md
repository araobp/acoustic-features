# Acoustic feature camera (STM32L4 with MEMS microphones)

This device is a sort of human ear: log-scale auditory perception and Fourier transform with Mel scaling as feature for training a brain. Connecting this device to Keras/TensorFlow mimics the human auditory system.

STM32L476RG as a core of this device seems a right choice, since the core of [STMicro's sensor tile](https://www.st.com/en/evaluation-tools/steval-stlkt01v1.html) is also STM32L476.

## STM32L4 configuration

The configuration below assumes [my original "Knowles MEMS mic Arduino shield"](https://github.com/araobp/acoustic-event-detection/tree/master/kicad).

- [CubeMX report](./acoustic_feature_camera.pdf) for STM32L476RG and the Arduino shield

## Making use of DMA

STMicro's HAL library supports "HAL_DFSDM_FilterRegConvHalfCpltCallback" that is very useful to implemente ring-buffer-like buffering for real-time processing.

I split buffers for DMA into two segments: segment A and segment B.

```
                                                  Interrupt
                          Clock                 ..............
                     +-+-------------+          : .......... :
                     | |             |          : :        V V
                     V |             |          : :   +-------------+
Sound/voice ))) [MEMS mic]-+-PDM->[DFSDM]-DMA->[A|B]->|             |->[A|B]->DMA->[DAC] --> Analog filter->head phone ))) Sound/Voice
                       V   |                          |ARM Cortex-M4|->[Feature]->DMA->[UART] --> Oscilloscope on PC or RasPi3
Sound/voice ))) [MEMS mic]-+                          |             |
                                                      +-------------+
```

All the DMAs are synchronized, because their master clock is the system clock.

## Sampling frequency

- The highest frequency on a piano is 4186Hz, but it generate overtones: ~10kHz.
- Human voice also generates overtones: ~ 10kHz.

So the sampling frequency of MEMS mic should be around 20kHz: 20kHz/2 = 10kHz ([Nyquist frequency](https://en.wikipedia.org/wiki/Nyquist_frequency))

## Parameters of DFSDM (digital filter for sigma-delta modulators) on STM32L4

- System clock: 80MHz
- Clock divider: 32
- FOSR/decimation: 128
- sinc filter: sinc3
- right bit shift: 6 (2 * 128^3 = 2^22, so 6-bit-right-shift is required to output 16bit PCM)
- Sampling frequency: 80_000_000/32/128 = 19.5kHz

## Pre-processing on STM32L4/CMSIS-DSP

```
   << MEMS mic >>
         |
         V
   DFSDM w/ DMA
         |
  [16bit PCM data] --> DAC w/ DMA for montoring the sound with a headset
         |
  float32_t data
         |
         |                .... CMSIS-DSP APIs() .........................................
  [ AC coupling  ]-----+  arm_mean_f32(), arm_offset_f32
         |             |
  [ Pre-emphasis ]-----+  arm_fir_f32()
         |             |
[Overlapping frames]   |  arm_copy_f32()
         |             |
  [Windowing(hann)]    |  arm_mult_f32()
         |             |
  [   Real FFT   ]     |  arm_rfft_fast_f32()
         |             |
  [     PSD      ]-----+  arm_cmplx_mag_f32(), arm_scale_f32()
         |             |
  [Filterbank(MFSCs)]--+  arm_dot_prod_f32()
         |             |
     [Log scale]-------+  arm_scale_f32() with log10 approximation
         |             |
 [DCT Type-II(MFCCs)]  |  my original "dct_f32()" function based on CMSIS-DSP
         |             |
         +<------------+
         |
 data the size of int8_t or int16_t (i.e., quantization)
         |
         V
    UART w/ DMA
         |
         V
<< Oscilloscope GUI >>
```

## Frame/stride/overlap

- number of samples per frame: 512
- length: 512/19.5kHz = 26.3msec
- stride: 13.2msec
- overlap: 50%(13.2msec)

```
  26.3msec          stride 13.2msec
  --- overlap dsp -------------
  [b0|a0]            a(1/2)
     [a0|a1]         a(2/2)
  --- overlap dsp -------------
        [a1|b0]      b(1/2)
           [b0|b1]   b(2/2)
  --- overlap dsp -------------
              :
```
## Mel filter bank

- The number of filters is 40. The reason is that most of the technical papers I have read uses 40 filters.
- The filter bank is applied to the spectrogram to extract MFSCs and MFCCs for training a neural network.
- I have developed [DCT Type-II function in C language based on CMSIS-DSP](https://github.com/araobp/stm32-mcu/tree/master/NUCLEO-F401RE/DCT) to calculate MFCCs on STM32 in real time.

## log10 processing time issue

PSD calculation uses log10 math function, but CMSIS-DSP does not support log10. log10 on the standard "math.h" is too slow. I tried math.h log10, and the time required for calculating log10(x) does not fit into the time slot of sound frame, so I decided to adopt [log10 approximation](../ipynb/log10%20fast%20approximation.ipynb). The approximation has been working perfect so far.

### Processing time (actual measurement)

In case of 1024 samples per frame:
- fir (cfft/mult/cifft/etc * 2 times): 17msec
- log10: 54msec
- log10 fast approximation: 1msec
- atan2: 53msec

Note: log10(x) = log10(2) * log2(x)

Reference: https://community.arm.com/tools/f/discussions/4292/cmsis-dsp-new-functionality-proposal

## Command over UART (USB-serial)

UART baudrate: 460800bps

```

        Sequence over UART(USB-serial)

    ARM Cortex-M4L                    PC
           |                          |
           |<-------- cmd ------------|
           |                          |
           |------ data output ------>|
           |                          |


Data is send in int8_t.

```

### Output

|cmd| description    | output size             | purpose               | transfer mode |
|---|----------------|-------------------------|-----------------------|-----------|
|1  | RAW_WAVE       | N x 1                   | Input to oscilloscope | one frame |
|2  | FFT            | N/2 x 1                 | Input to oscilloscope | one frame |
|3  | SPECTROGRAM    | N/2 x 200               | Input to oscilloscope | streaming |
|4  | FEATURES       | NUM_FILTERS x 400       | Input to ML           | buffered  |

### Pre-emphasis

|cmd| description    | output size             | purpose               |
|---|----------------|-------------------------|-----------------------|
|P  | Enable pre-emphasis |                    |                       |
|p  | Disable pre-emphasis |                   |                       |

### Data format of features

The PC issues "FEATURES" command to the device to fetch features that are the last 2.6sec MFSCs and MFCCs buffered in a memory.

```
      shape: (200, 40, 1)       shape: (200, 40, 1)
   +------------------------+------------------------+
   |    MFSCs (40 * 200)    |    MFCCs (40 * 200)    |
   +------------------------+------------------------+
```

The GUI flatten features and convert it into CSV to save it as a csv file in a dataset folder.

## Beam forming 

Although I developed beam forming, it takes too much cost for tuning. So I removed it, and the code remains in [this "old" folder](../acoustic_feature_camera_old).
