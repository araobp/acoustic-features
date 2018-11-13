# IoT network

```
Sound/voice ))) [MEMS mic]-[DFSDM][ARM Cortex-M4(STM32L4)]--BLE/LPWA/5G--+
                                                                         |
Sound/voice ))) [MEMS mic]-[DFSDM][ARM Cortex-M4(STM32L4)]--BLE/LPWA/5G--+---------> Cloud
                                                                         |
Sound/voice ))) [MEMS mic]-[DFSDM][ARM Cortex-M4(STM32L4)]--BLE/LPWA/5G--+
                                     |           [DAC]
                                   UART            |
                                     |             |
                                 (VCP/USB)    [Analog filter] --> head phone for monitoring sound from mic (for debugging purpose only)
                                  (or BLE)
                                     |
                                     v
                           [Oscilloscope GUI(Tk)] --- features ---> PC for training CNN
```

