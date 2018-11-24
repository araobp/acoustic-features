# Acoustic Event Detection with STM32L4/Keras/TensorFlow

![](./oscilloscope/screenshots/spectrogram(psd)_small.jpg)

## Background and motivation

If you are interested in "edge AI", extracting good feature (i.e., seeking the best feature quantization model) is as important as modeling a good CNN, since your CNN should be small enough to fit into a limited amount of RAM memory size (e.g., 128Kbyes).

At first, I am experimenting to see if pre-processing for edge AI fit into RAM on Arm Cortex-M MCU.

Also I am developing a tool "oscilloscope" to visualize how data is processed at every stage in the pre-processing pipeline. Such a tool is useful to seek the best quantization model for every use cases. For example, the picture above is a capture of Tin Whistle music. Squre wave form is seen on the picutre at several points which can be "good feature" for training CNN.

Currently, I am using the device and the tool to train CNN on Keras/TensorFlow for AED (Acoustic Event Detection).

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
                                            +---> [agent.py/RasPi3] ---> Cloud
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
