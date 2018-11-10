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

=> [Platform and tool chain](./PLATFORM.md]

## IoT network

=> [IoT network](./NETWORK.md)

## Edge device for machine learning (STM32L4)

=> [Edge device for machine learning](./stm32)

## Oscilloscope GUI with the edge device to acquire data for training CNN

=> [Oscilloscope GUI implementation on matplotlib/Tkinter](./oscilloscope)

## CNN experiments with Keras/TensorFlow

=> [CNN experiments with Keras/TensorFlow](./tensorflow)
