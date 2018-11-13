# IoT network

Note: "BLE" in the picture below should be replaced with either LPWA or 5G in future.

```
Sound/voice ))) [MEMS mic]-[DFSDM][ARM Cortex-M4(STM32L4)]--BLE--+
                                                                 |
Sound/voice ))) [MEMS mic]-[DFSDM][ARM Cortex-M4(STM32L4)]--BLE--+---------> Cloud
                                                                 |
Sound/voice ))) [MEMS mic]-[DFSDM][ARM Cortex-M4(STM32L4)]--BLE--+
                                     |           [DAC]
                                   UART            |
                                     |             |
                                 (VCP/USB)    [Analog filter] --> head phone for monitoring sound from mic (for debugging purpose only)
                                  (or BLE)
                                     |
                                     v
                           [Oscilloscope GUI(Tk)] --- features ---> PC for training CNN
```

