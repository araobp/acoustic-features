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

CubeMX.AI will be available in 1Q/2019: https://community.st.com/s/question/0D50X00009yG1AUSA0/when-is-stm32cubeai-available
