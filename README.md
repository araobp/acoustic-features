# Acoustic Event Detection with STM32L4/Keras/TensorFlow

![](./oscilloscope/screenshots/spectrogram(psd)_small.jpg)

## Background and motivation

I need to collect a lot of data for training CNN(Convolutional Neural Network), but it is a very time-consuming work, so I decided to develop a data collecting device ("audio camera") for automation of the work.

Since Arm has already released [CMSIS-NN](http://www.keil.com/pack/doc/CMSIS_Dev/NN/html/index.html) and STMicro is going to release [CubeMX.AI](https://www.st.com/content/st_com/en/about/innovation---technology/artificial-intelligence.html), I decided to implement most of the pre-processing for CNN on the edge device: STM32L476RG.

I use Keras/TensorFlow for training CNN with the data acquired by the device via Oscillosope GUI.

## Use cases

- musical instruments recognition
- human activity recognition

## Architecture and platform

- [Network architecture](./NETWORK.md)
- [Platform and tool chain](./PLATFORM.md)

## AED system components in development

- [Edge device for machine learning (CubeMX/TrueSTUDIO)](./stm32)
- [Oscilloscope GUI implementation on matplotlib/Tkinter (Python)](./oscilloscope)
- [Arduino shield of two MEMS microphones with beam forming support (KiCAD)](./kicad)
- Mobile IoT gateway: "UART over BLE" to "REST over WiFi" (ESP32-based)
- Database on the cloud: Node.js/Express/MongoDB-based => I will reuse [the output of this project](https://github.com/araobp/api-server).

Note: BLE module should be replaced with 5G module in future, to simplify the architecture.

## CNN experiments

- [CNN experiments with Keras/TensorFlow](./tensorflow)
