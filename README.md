# Acoustic Event Detection with STM32L4 and TensorFlow

![](./oscilloscope/screenshots/spectrogram(psd).jpg)

Framenco (Bulerias)

## Background and motivation

Although AI is booming, most of AI researchers use open data on the web for training a neural network. However, I focus on paticular AED(Acoustic Event Detection) use cases for myself, and I need to collect a lot of data by myself. It is a very time-consuming work, so I need to develop a data collecting device ("audio camera").

Use cases:
- musical instruments recognition
- human activity recognition

## Development 

- [IoT network architecture](./NETWORK.md)
- [Platform and tool chain](./PLATFORM.md)
- [Edge device for machine learning](./stm32)
- [Oscilloscope GUI implementation on matplotlib/Tkinter](./oscilloscope)

## CNN experiments

- [CNN experiments with Keras/TensorFlow](./tensorflow)
