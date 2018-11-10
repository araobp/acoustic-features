# Acoustic Event Detection with STM32L4 and TensorFlow

![](./oscilloscope/screenshots/spectrogram(psd).jpg)

Framenco (Bulerias)

## Background and motivation

Although AI is booming, most of AI researchers use open data on the web for training a neural network. However, I focus on special AED(Acoustic Event Detection) use cases for myself, and I need to collect a lot of data by myself. It is a very time-consuming work, so I need to develop a data collecting device ("audio camera") that satisfies the following requirements:

- visualize sound in real-time: raw wave, FFT, spectrogram/mel-spectrogram and MFCCs.
- optimize parameters of MEMS mic parameters (DFSDM parameters) and filter/transform functions (pre-processing) to obtain the best sound image (mel-spectrogram) for training convolution layers of CNN.
- perform pre-processing on the edge: low-pass filtering, pre-emphasis and mel-spectorgram.
- collect data/image as an input to CNN.
- use the data collection device as an IoT edge device for deploying a trained CNN.
- low power consumption and small size.
- workable with BLE/CAN/LoRa
- free development tools avaiable for developing the edge device.

Starting point of this project is this paper: [CNN Architectures for Large-Scale Audio Classification](https://arxiv.org/abs/1609.09430)

However, I pursue small-scale audio classification of particular use cases for myself:
- musical instruments recognition
- human activity recognition

## Platform and tool chain

#### Platform

STMicro STM32L4 (ARM Cortex-M4 with DFSDM, DAC, UART etc) is an all-in-one MCU that satisfies all the requirements above:
- [STMicro NUCLEO-L476RG](https://www.st.com/en/evaluation-tools/nucleo-l476rg.html): STM32L4 development board
- [STMicro X-NUCLEO-CCA02M1](https://www.st.com/en/ecosystems/x-nucleo-cca02m1.html): MEMS mic evaluation board

In addition, I use Knowles MEMS mics SPM0405HD4H to add extra mics to the platform above (for beam forming etc).

I already developed [an analog filter (LPF and AC couping)](https://github.com/araobp/stm32-mcu/tree/master/analog_filter) to monitor sound from DAC in real-time.

#### Tool chain

- STMicro's [CubeMX](https://www.st.com/en/development-tools/stm32cubemx.html) and [TrueSTUDIO(Eclipse/GCC/GDB)](https://atollic.com/truestudio/) for firmware development.
- Jupyter Notebook for simulation.
- IDLE and numpy/pandas/matplotlib/Tkinter for developing Oscilloscope GUI.
- Google's Colab to train CNN.

## IoT network

```
Sound/voice ))) [MEMS mic]-[DFSDM][ARM Cortex-M4(STM32L4)]--LPWA/5G--+
                                                                     |
Sound/voice ))) [MEMS mic]-[DFSDM][ARM Cortex-M4(STM32L4)]--LPWA/5G--+---------> Database
                                                                     |
Sound/voice ))) [MEMS mic]-[DFSDM][ARM Cortex-M4(STM32L4)]--LPWA/5G--+
                                     |           [DAC]
                                     |             |
                                 USB serial     [Analog filter] --> head phone for monitoring sound from mic
                                     |
                                     v
                           [Oscilloscope GUI(Tk)] --- features ---> PC for training CNN
```

Refer to this page for the analog filter: https://github.com/araobp/stm32-mcu/tree/master/analog_filter

## Edge device for machine learning (STM32L4)

=> [Edge device for machine learning](./stm32)

## Oscilloscope GUI with the edge device to acquire data for training CNN

=> [Oscilloscope GUI implementation on matplotlib/Tkinter](./oscilloscope)

## CNN experiments with Keras/TensorFlow

=> [CNN experiments with Keras/TensorFlow](./tensorflow)
