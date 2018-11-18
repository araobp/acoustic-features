# Network architecture

```
Sound/voice ))) [MEMS mic]-[DFSDM][ARM Cortex-M4(STM32L4)]
                                     |           [DAC]
                                   UART            |
                                     |             |
                                 (VCP/USB)    [Analog filter] --> head phone for monitoring sound from mic (for debugging purpose only)
                                  (or BLE)
                                     |
                                     |
                                     +---> [Oscilloscope GUI(Tk)] --- features ---> Keras/TensorFlow on Jupyter for training CNN
                                     |
                                     +---> [agent.py/RasPi] (I will use RasPi until CubeMX.AI has been available)
```
