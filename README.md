# Acoustic Event Detection with STM32L4/Keras/TensorFlow

## Background and motivation

I need to collect a lot of data for training CNN(Convolutional Neural Network), but it is a very time-consuming work, so I decided to develop a data collecting device ("audio camera") for automation of the work.

Since STMicro is going to release [CubeMX.AI](https://www.st.com/content/st_com/en/about/innovation---technology/artificial-intelligence.html), I decided to implement most of the pre-processing for CNN on the edge device: STM32L476RG.

I use Keras/TensorFlow for training CNN with the data acquired by the device via Oscillosope GUI.

## Use cases

- musical instruments recognition
- human activity recognition

## Architecture and platform

- [IoT network architecture](./NETWORK.md)
- [Platform and tool chain](./PLATFORM.md)

## AED system components in development

- [Edge device for machine learning (CubeMX/TrueSTUDIO)](./stm32)
- [Oscilloscope GUI implementation on matplotlib/Tkinter (Python)](./oscilloscope)
- [Arduino shield of two MEMS microphones and Microchip RN4020 BLE module (KiCAD)](./kicad)
- [Mobile IoT gateway: "UART over BLE" to "MQTT over WiFi" (ESP32-based)]

## CNN experiments

- [CNN experiments with Keras/TensorFlow](./tensorflow)
