# Arduino shield with two Knowles MEMS microphones (PDM)

This is a ultra-cheap MEMS mic shield for edge AI. The total cost of all the parts is around $10.

![](../stm32/beam_forming_20mm_board.jpg)

## Beam forming support

The board is equipped with two MEMS mics, and the distance between mic1 and mic2 is 20mm.

The reason why the distance is 20mm:

- the distance is good for acoustic event detection.
- 20mm = 2.54mm * 8, that is, it is suitable for DIP.

## Parts

- [Knowles SPM0405HD4H MEMS microphones](http://akizukidenshi.com/catalog/g/gM-05577/)
- [Universal board](http://akizukidenshi.com/catalog/g/gP-07555/)

## Schematic

- [schematic](./arduino_shield.pdf)
