# Acoustic Event Detection with STM32L4/Keras/TensorFlow

![](./oscilloscope/screenshots/spectrogram(psd)_small.jpg)

## Background and motivation

I need to collect a lot of data for training CNN(Convolutional Neural Network), but it is a very time-consuming work, so I decided to develop a data collecting device ("audio camera") for automation of the work.

Since Arm has already released [CMSIS-NN](http://www.keil.com/pack/doc/CMSIS_Dev/NN/html/index.html) and STMicro is going to release [CubeMX.AI](https://www.st.com/content/st_com/en/about/innovation---technology/artificial-intelligence.html), I decided to implement most of the pre-processing for CNN on the edge device: STM32L476RG.

I use Keras/TensorFlow for training CNN with the data acquired by the device via Oscillosope GUI.

## Use cases

- musical instruments recognition
- human activity recognition
- always-on speech recogniton (e.g., "OK Google")

## Architecture

```
                                          ARM Cortex-M4(STM32L476RG)
                                      ....................................
                                      :   Filters for feature extraction :
Sound/voice ))) [MEMS mic]--PDM-->[DFSDM]--+->[]->[]->[]->[]---+         :
                                      :    |                   |         :
                                      :    +------------+      |         :
                                      :     +-----------|------+         :
                                      :     |           |                :
                                      :     V           V                :
                                      :..[USART]......[DAC]..............:
                                            |           |
                                            |           | *** monitoring ***
                                            |           +---> [Analog filter] --> head phone
                                       (features)
                                            |
                                            | *** learning ***
                                            +---> [Oscilloscope GUI(Tk)] --- (data set) ---> Keras/TensorFlow
                                            |
                                            | *** inference ***
                                            +---> [agent.py/RasPi3] (to replaced with CubeMX.AI in future)
                                            :
                                            : *** inference (Note: *1) ***
                                            +- -> [CubeMX.AI/STM32] ---> [Communication module] ---> Cloud
```

*1 CubeMX.AI will be available in 1Q/2019: https://community.st.com/s/question/0D50X00009yG1AUSA0/when-is-stm32cubeai-available

## Platform

- [Platform and tool chain](./PLATFORM.md)

## AED system components in development

- [Edge device for machine learning (CubeMX/TrueSTUDIO)](./stm32)
- [Oscilloscope GUI implementation on matplotlib/Tkinter (Python)](./oscilloscope)
- [Arduino shield of two MEMS microphones with beam forming support (KiCAD)](./kicad)

## CNN experiments

- [CNN experiments with Keras/TensorFlow](./tensorflow)
