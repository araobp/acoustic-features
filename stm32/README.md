# Edge device for machine learning (STM32L4)

### Making use of DMA

STMicro's HAL library supports "HAL_DFSDM_FilterRegConvHalfCpltCallback" that is very useful to implemente ring-buffer-like buffering for real-time processing.

I splitted buffers for DMA into two segments: segment A and segment B.

```
Sound/voice ))) [MEMS mic]-PDM->[DFSDM]-DMA->[A|B]->[ARM Cortex-M4]
                                                    [ARM Cortex-M4]->[A|B]->DMA->[UART] --- > PC(pyserial)
                                                    [ARM Cortex-M4]->[A|B]->DMA->[DAC] ))) Sound/Voice

```

All the DMAs are synchronized, because their master clock is the system clock.

### Sampling frequency

- The highest frequency on a piano is 4186Hz, but it generate overtones: ~10kHz.
- Human voice also generates overtones: ~ 10kHz.

So the sampling frequency of MEMS mic should be around 20kHz: 20kHz/2 = 10kHz ([Nyquist frequency](https://en.wikipedia.org/wiki/Nyquist_frequency))

### Parameters of DFSDM (digital filter for sigma-delta modulators) on STM32L4

- System clock: 80MHz
- Clock divider: 32
- FOSR/decimation: 128
- sinc filter: sinc3
- right bit shift: 3 (2 * 128^3 = 2^22, so 6-bit-right-shift is required to output 16bit PCM)
- Sampling frequency: 80_000_000/32/128 = 19.5kHz

#### Pre-processing on STM32L4/CMSIS-DSP

```
      MEMS mic
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
  [Windowins(hann)]    |  arm_mult_f32()
         |             |
  [   Real FFT   ]     |  arm_rfft_fast_f32()
         |             |
  [     PSD      ]-----+  arm_cmplx_mag_f32(), arm_scale_f32()
         |             |
  [Mel-spectrogram]----+  arm_dot_prod_f32()
         |             |
 [DCT Type-II(MFCCs)]  |  arm_rfft_fast_f32(), arm_scale_f32(), arm_cmplx_mult_cmplx_f32()
         |             |
         +<------------+
         |
 data the size of int8_t (in ASCII)
         |
         V
    UART w/ DMA
         |
         V
Oscilloscope GUI/IoT gateway
```

- My conclusion is that 80_000_000(Hz)/64(clock divider)/64(FOSR) with pre-emphasis(HPF) is the best setting for obtaining the best images of mel-spectrogram.
- I use a triangler filter bank to obtain mel-spectrogram, and I make each triangle filter having a same amount of area.

### Frame/stride/overlap

- number of samples per frame: 512
- length: 512/19.5kHz = 26.3msec
- stride: 13.2msec
- overlap: 50%(13.2msec)

```
26.3msec         stride
[b0|a1]            1a --> mel-scale spectrogram via filter bank or 12 MFCCs
   [a1|b1]         1b --> mel-scale spectrogram via filter bank or 12 MFCCs
      [b1|a2]      2a --> mel-scale spectrogram via filter bank or 12 MFCCs
         [a2|b2]   2b --> mel-scale spectrogram via filter bank or 12 MFCCs
            :
```
### Filter banks

Mel-scale spectrogram is used for training CNN

- Mel-scale: 40 filters (512 samples divided by (40 + 1))
- Linear-scale: 255 filters (512 samples divide by (255 + 1))

### log10 processing time issue

PSD caliculation uses log10 math function, but CMSIS-DSP does not support log10. log10 on the standard "math.h" is too slow. I tried math.h log10, and the time required for caluculating log10(x) does not fit into the time slot of sound frame, so I decided to adopt [log10 approximation](../ipynb/log10%20fast%20approximation.ipynb). The approximation has been working perfect so far.

### Processing time (actual measurement)

In case of 1024 samples per frame:
- fir (cfft/mult/cifft/etc * 2 times): 17msec
- log10: 54msec
- log10 fast approximation: 1msec
- atan2: 53msec

Note: log10(x) = log10(2) * log2(x)

Reference: https://community.arm.com/tools/f/discussions/4292/cmsis-dsp-new-functionality-proposal

## Beam forming

Beam forming should improve SNR at five directions as follows:

```

left                            right
      /                    /
     /                    /
    /                    /
   / )) theta           /
 [M1]                 [M2]
   <------- l --------->

f_s = 80_000_000 / 32 / 128 = 19.5kHz
s = 343 / f_s = 0.0176m = 17.6mm (length of one-sample shift)
l = 40mm (distance between Mic1 and Mic2)

theta_left2 = arccos(-17.6*2/40.0) = 2.65[rad] = 152[degrees]
theta_left1 = arccos(-17.6/40.0) = 2.03[rad] = 116[degrees]
theta_center = pi/2 rad = 90[degrees]
theta_right1 = arccos(17.6/40.0) = 1.12[rad] = 64[degrees]
theta_right2 = arccos(17.6*2/40.0) = 0.50[rad] = 28[degrees]

```

|direction|degrees|
|---------|-------|
|left2    |152    |
|left1    |116    |
|center   |90     |
|right1   |64     |
|right2   |28     |

### Command over UART (USB-serial)

UART baudrate: 921600bps

```

        Sequence over UART(USB-serial)

    ARM Cortex-M4L                    PC
           |                          |
           |<-------- cmd ------------|
           |                          |
           |------ data output ------>|
           |                          |


Data is send in ASCII characters, and the data format is as follows:

d: data delimiter
e: data transmission end

1,2,3,4,d,...,5,6,7,8,d\n
9,10,11,12,d,...,13,14,15,16,d\n
17,18,19,20,d,...,21,22,23,24,e\n

```

#### Output

|cmd|description     | output size             | purpose               |
|---|----------------|-------------------------|-----------------------|
|0  | RAW_WAVE       | N x 1                   | Input to oscilloscope |
|1  | PSD            | N/2 x 1                 | Input to ML           |
|2  | FILTERBANK     | N/6 x NUM_FILTERS       | (for testing)         |
|3  | FILTERED_MEL   | NUM_FILTERS x 200       | Input to ML           |
|4  | MFCC           | NUM_FILTERS x 200       | Input to ML           |
|5  | MFCC_STREAMING | NUM_FILTERS x 07fffffff | (for testing)         |
|6  | FILTERED_LINEAR| NUM_FILTERS x 200       | Input to ML           |

#### Pre-emphasis

|cmd|description     | output size             | purpose               |
|---|----------------|-------------------------|-----------------------|
|P  | Enable pre-emphasis |                    |                       |
|p  | Disable pre-emphasis |                   |                       |

#### Beam forming

|cmd|description     | output size             | purpose               |
|---|----------------|-------------------------|-----------------------|
|L  | theta left2    |                         |                       |
|l  | theta left1    |                         |                       |
|c  | theta center   |                         |                       |
|r  | theta right1   |                         |                       |
|R  | theta right2   |                         |                       |
