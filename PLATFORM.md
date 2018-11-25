# Platform and tool chain

## Platform

### Main board

STMicro STM32L4 (ARM Cortex-M4 with DFSDM, DAC, UART etc) is an all-in-one MCU that satisfies all the requirements of this project:
- [STMicro NUCLEO-L476RG](https://www.st.com/en/evaluation-tools/nucleo-l476rg.html): STM32L4 development board

### My original Arduino shield

I use two MEMS microphones from Knowles:
- [README and the schematic of the shield](./kicad)

### Analog filter for DAC: LPF and AC coupling

[Analog filter (LPF and AC couping)](https://github.com/araobp/stm32-mcu/tree/master/analog_filter) is optionally used for monitoring sound with a head phone.

### Application processor (host MCU/MPU)

- I use Win10 PC as an application processor for developing this system. 
- I also use RasPi for CNN training and CNN inference for the time being: all the pre-proccessing is performed on STM32L4 and another STM32L4 or F4 will be added to the system for CNN inference in future.

## Tool chain

- STMicro's [CubeMX](https://www.st.com/en/development-tools/stm32cubemx.html) and [TrueSTUDIO(Eclipse/GCC/GDB)](https://atollic.com/truestudio/) for firmware development.
- Jupyter Notebook for simulation.
- IDLE and numpy/pandas/matplotlib/Tkinter for developing Oscilloscope GUI.
- Google's Colab to train CNN.

