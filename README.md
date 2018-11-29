# Acoustic Event Detection with STM32L4/Keras/TensorFlow

![](./oscilloscope/screenshots/spectrogram(psd)_small.jpg)

## Background and motivation

I am just interested in Acoustic Event Detection (AED) on "edge AI": ["New Architectures Bringing AI to the Edge"](https://www.eetimes.com/document.asp?doc_id=1333920).

## Project status (Nov 29, 2018)

- All the pre-processing features and the oscilloscope GUI have been implemented.
- Several CNN models on Keras/TensorFlow have already been tested.

*** I will come back to this project after CubeMX AI has been released (1Q/2018) ***

## AED system

Architecture:

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

Platform:
- [Platform and tool chain](./PLATFORM.md)

## System components

- [Edge device for deep learning (CubeMX/TrueSTUDIO)](./stm32)
- [Arduino shield of two MEMS microphones with beam forming support (KiCAD)](./kicad)
- [Oscilloscope GUI implementation on matplotlib/Tkinter (Python)](./oscilloscope)

## Use cases of AED on edge AI

I apply the system to potential edge AI use cases:
- musical instrument recognition and music performance analysis
- human activity recognition
- always-on automatic speech recogniton (e.g., "OK Google")
- automatic questionnaire collection in a restaurant
- bird recognition

### CNN experiments 

- [CNN experiments with Keras/TensorFlow](./tensorflow)
