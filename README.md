# Acoustic Event Detection with STM32L4 and TensorFlow

![](./oscilloscope/screenshots/spectrogram(psd).jpg)

Framenco (Bulerias)

## Background and motivation

I need to collect a lot of data for training CNN(Convolutional Neural Network), but it is a very time-consuming work, so I decided to develop a data collecting device ("audio camera") for automation of the work.

Since STMicro is going to release [CubeMX.AI](https://www.st.com/content/st_com/en/about/innovation---technology/artificial-intelligence.html), I decided to implement all the pre-processing for CNN on the edge device: STM32L476RG.

## Use cases

- musical instruments recognition
- human activity recognition

## Development 

- [IoT network architecture](./NETWORK.md)
- [Platform and tool chain](./PLATFORM.md)
- [Edge device for machine learning](./stm32)
- [Oscilloscope GUI implementation on matplotlib/Tkinter](./oscilloscope)

## CNN experiments

- [CNN experiments with Keras/TensorFlow](./tensorflow)
