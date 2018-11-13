# Acoustic Event Detection with STM32L4/Keras/TensorFlow

![](./oscilloscope/screenshots/spectrogram(psd)_small.jpg)

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
- SNR improvement with beam forming.
- Mobile IoT gateway: "UART over BLE" to "REST over WiFi" (ESP32-based)
- Database on the cloud: Node.js/Express/MongoDB-based => I will reuse [the output of this project](https://github.com/araobp/api-server).

Note: BLE module should be replaced with 5G module in future, to simplify the architecture.

## CNN experiments

- [CNN experiments with Keras/TensorFlow](./tensorflow)

## Beam forming

```
      /                    /
     /                    /
    /                    /
   / )) theta           /
 [M1]                 [M2]
   <------- l --------->

f_s = 80_000_000 / 32 / 128 = 19.5kHz
s = 343 / f_s = 0.0176m = 17.6mm (length of one-sample shift)
l = 40mm (distance between Mic1 and Mic2)

theta_0 = pi/2 rad = 90 degrees
theta_1 = arccos(17.6/40.0) = 1.12[rad] = 64[degrees]
theta_2 = arccos(17.6*2/40.0) = 0.50[rad] = 28[degrees]
```
