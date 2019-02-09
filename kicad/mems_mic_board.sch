EESchema Schematic File Version 2
LIBS:power
LIBS:device
LIBS:switches
LIBS:relays
LIBS:motors
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:mcu
LIBS:mems_mic_board-cache
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "MEMS mic shield"
Date "2018-11-25"
Rev "ver 0.2"
Comp "https://github.com/araobp"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L mems_mic U2
U 1 1 5BEA0916
P 5400 2850
F 0 "U2" H 5400 2550 60  0000 C CNN
F 1 "mems_mic" H 5350 3150 60  0000 C CNN
F 2 "mcu:MEMS_mic" H 5400 2850 60  0001 C CNN
F 3 "" H 5400 2850 60  0001 C CNN
	1    5400 2850
	1    0    0    -1  
$EndComp
$Comp
L mems_mic U3
U 1 1 5BEA0942
P 5400 3750
F 0 "U3" H 5400 3450 60  0000 C CNN
F 1 "mems_mic" H 5350 4050 60  0000 C CNN
F 2 "mcu:MEMS_mic" H 5400 3750 60  0001 C CNN
F 3 "" H 5400 3750 60  0001 C CNN
	1    5400 3750
	1    0    0    -1  
$EndComp
$Comp
L +3.3V #PWR01
U 1 1 5BEA0B18
P 6300 950
F 0 "#PWR01" H 6300 800 50  0001 C CNN
F 1 "+3.3V" H 6300 1090 50  0000 C CNN
F 2 "" H 6300 950 50  0001 C CNN
F 3 "" H 6300 950 50  0001 C CNN
	1    6300 950 
	1    0    0    -1  
$EndComp
NoConn ~ 5900 2800
NoConn ~ 5900 2900
NoConn ~ 5900 3700
NoConn ~ 5900 3800
NoConn ~ 4900 3800
NoConn ~ 4900 2900
$Comp
L GND #PWR02
U 1 1 5BEA0B85
P 4500 6200
F 0 "#PWR02" H 4500 5950 50  0001 C CNN
F 1 "GND" H 4500 6050 50  0000 C CNN
F 2 "" H 4500 6200 50  0001 C CNN
F 3 "" H 4500 6200 50  0001 C CNN
	1    4500 6200
	1    0    0    -1  
$EndComp
NoConn ~ 8050 2000
NoConn ~ 8050 2100
NoConn ~ 8050 2200
NoConn ~ 8050 2300
NoConn ~ 8050 2400
NoConn ~ 8050 2500
NoConn ~ 8050 2700
Text Notes 8300 2650 0    60   ~ 0
PC7 (DFSDM_DATAIN2)
$Comp
L Conn_01x08_Male J5
U 1 1 5BEA0DD0
P 8250 5450
F 0 "J5" H 8250 5850 50  0000 C CNN
F 1 "Conn_01x08_Male" H 8250 4950 50  0000 C CNN
F 2 "mcu:Pin Header 8P" H 8250 5450 50  0001 C CNN
F 3 "" H 8250 5450 50  0001 C CNN
	1    8250 5450
	-1   0    0    -1  
$EndComp
Text Notes 8300 5800 0    60   ~ 0
USART_TX
Text Notes 8300 5900 0    60   ~ 0
USART_RX
NoConn ~ 8050 5150
NoConn ~ 8050 5250
NoConn ~ 8050 5350
NoConn ~ 8050 5450
NoConn ~ 8050 5550
NoConn ~ 8050 5650
$Comp
L Conn_01x06_Male J2
U 1 1 5BEA152F
P 2400 5550
F 0 "J2" H 2400 5850 50  0000 C CNN
F 1 "Conn_01x06_Male" H 2400 5150 50  0000 C CNN
F 2 "mcu:Pin Header 6P" H 2400 5550 50  0001 C CNN
F 3 "" H 2400 5550 50  0001 C CNN
	1    2400 5550
	1    0    0    -1  
$EndComp
NoConn ~ 2600 5350
NoConn ~ 2600 5450
NoConn ~ 2600 5550
NoConn ~ 2600 5650
NoConn ~ 2600 5750
NoConn ~ 2600 5850
Text Notes 2500 2650 0    60   ~ 0
Vin
Text Notes 2150 2550 0    60   ~ 0
Vin
Text Notes 2150 2450 0    60   ~ 0
GND
Text Notes 2150 2350 0    60   ~ 0
GND
Text Notes 2150 2150 0    60   ~ 0
3.3V
Text Notes 2100 2050 0    60   ~ 0
RESET
$Comp
L tactile_sw U1
U 1 1 5BEA1A70
P 3650 1050
F 0 "U1" V 3350 900 60  0000 C CNN
F 1 "tactile_sw" V 3900 1050 60  0000 C CNN
F 2 "mcu:tactile_sw_4p" V 3700 1100 60  0001 C CNN
F 3 "" V 3700 1100 60  0001 C CNN
	1    3650 1050
	0    1    1    0   
$EndComp
Wire Wire Line
	5900 3000 6600 3000
Wire Wire Line
	6600 2600 6600 3900
Wire Wire Line
	6600 3900 5900 3900
Wire Wire Line
	3900 3900 4900 3900
Wire Wire Line
	4900 3000 4300 3000
Wire Wire Line
	4300 3000 4300 3900
Connection ~ 4300 3900
Wire Wire Line
	6300 2700 5900 2700
Wire Wire Line
	6300 950  6300 3600
Wire Wire Line
	6300 3600 5900 3600
Connection ~ 6300 2700
Wire Wire Line
	4900 3600 4500 3600
Wire Wire Line
	4500 2700 4500 6200
Wire Wire Line
	4900 2700 4500 2700
Connection ~ 4500 3600
Wire Wire Line
	4900 3700 4500 3700
Connection ~ 4500 3700
Wire Wire Line
	4900 2800 4750 2800
Wire Wire Line
	4750 2800 4750 2400
Wire Wire Line
	4750 2400 6300 2400
Connection ~ 6300 2400
Wire Wire Line
	2600 2000 3000 2000
Wire Wire Line
	3000 2000 3000 1150
Wire Wire Line
	3000 1150 3350 1150
$Comp
L GND #PWR03
U 1 1 5BEA39CA
P 4300 1700
F 0 "#PWR03" H 4300 1450 50  0001 C CNN
F 1 "GND" H 4300 1550 50  0000 C CNN
F 2 "" H 4300 1700 50  0001 C CNN
F 3 "" H 4300 1700 50  0001 C CNN
	1    4300 1700
	1    0    0    -1  
$EndComp
Wire Wire Line
	4050 1150 4300 1150
Wire Wire Line
	2600 2300 3450 2300
Wire Wire Line
	3450 2300 3450 4200
Wire Wire Line
	3450 4200 4500 4200
Connection ~ 4500 4200
Wire Wire Line
	3900 3900 3900 6250
Wire Wire Line
	2600 2100 6300 2100
Connection ~ 6300 2100
Wire Wire Line
	8050 2600 6600 2600
Connection ~ 6600 3000
$Comp
L PWR_FLAG #FLG04
U 1 1 5BEA4D7E
P 6700 1200
F 0 "#FLG04" H 6700 1275 50  0001 C CNN
F 1 "PWR_FLAG" H 6700 1350 50  0000 C CNN
F 2 "" H 6700 1200 50  0001 C CNN
F 3 "" H 6700 1200 50  0001 C CNN
	1    6700 1200
	1    0    0    -1  
$EndComp
$Comp
L PWR_FLAG #FLG05
U 1 1 5BEA4DA6
P 4850 5900
F 0 "#FLG05" H 4850 5975 50  0001 C CNN
F 1 "PWR_FLAG" H 4850 6050 50  0000 C CNN
F 2 "" H 4850 5900 50  0001 C CNN
F 3 "" H 4850 5900 50  0001 C CNN
	1    4850 5900
	1    0    0    -1  
$EndComp
Wire Wire Line
	6700 1200 6700 1400
Wire Wire Line
	6700 1400 6300 1400
Connection ~ 6300 1400
Wire Wire Line
	4850 5900 4850 6000
Wire Wire Line
	4850 6000 4500 6000
Connection ~ 4500 6000
Wire Wire Line
	4300 1150 4300 1700
Text Notes 3950 7450 1    60   ~ 0
PC2 (DFSDM_CKOUT)
Connection ~ 4500 5400
Text Notes 2200 2250 0    60   ~ 0
5V\n
NoConn ~ 2600 2400
NoConn ~ 2600 2500
$Comp
L Conn_01x01_Male J3
U 1 1 5BEA9234
P 3900 6450
F 0 "J3" H 3900 6550 50  0000 C CNN
F 1 "Conn_01x01_Male" H 3900 6350 50  0000 C CNN
F 2 "mcu:Pin_header_1P" H 3900 6450 50  0001 C CNN
F 3 "" H 3900 6450 50  0001 C CNN
	1    3900 6450
	0    -1   -1   0   
$EndComp
NoConn ~ -1000 1500
NoConn ~ -950 1450
Text Notes 4950 3200 0    60   ~ 0
Mic R
Text Notes 4950 4100 0    60   ~ 0
Mic L
NoConn ~ 8050 5750
NoConn ~ 8050 5850
NoConn ~ 2600 2200
$Comp
L Conn_01x08_Male J1
U 1 1 5C5A0EE3
P 2400 2100
F 0 "J1" H 2400 2500 50  0000 C CNN
F 1 "Conn_01x08_Male" H 2400 1600 50  0000 C CNN
F 2 "mcu:Pin Header 8P" H 2400 2100 50  0001 C CNN
F 3 "" H 2400 2100 50  0001 C CNN
	1    2400 2100
	1    0    0    -1  
$EndComp
NoConn ~ 2600 1800
NoConn ~ 2600 1900
$Comp
L Conn_01x10_Male J4
U 1 1 5C5A0FF3
P 8250 2200
F 0 "J4" H 8250 2700 50  0000 C CNN
F 1 "Conn_01x10_Male" H 8250 1600 50  0000 C CNN
F 2 "mcu:Pin Header 10P" H 8250 2200 50  0001 C CNN
F 3 "" H 8250 2200 50  0001 C CNN
	1    8250 2200
	-1   0    0    -1  
$EndComp
NoConn ~ 8050 1900
NoConn ~ 8050 1800
NoConn ~ 3350 950 
NoConn ~ 4050 950 
$EndSCHEMATC
