/*
 * lcd.c
 *
 *  Created on: 2019/02/11
 */

#include "lcd.h"

const uint16_t lcd_i2c_addr = LCD_I2C_ADDRESS << 1;

I2C_HandleTypeDef *phi2c;

/*
 * AQM1602XA-RN-GBW
 * LCD write command
 */
void write_command(uint8_t command) {
  uint8_t buf[2] = { 0x00, 0x00 };
  buf[1] = command;
  HAL_I2C_Master_Transmit(phi2c, lcd_i2c_addr, buf, 2, 100);
  HAL_Delay(1);
}

/*
 * AQM1602XA-RN-GBW
 * LCD write data
 */
void write_data(uint8_t data) {
  uint8_t buf[2] = { 0x40, 0x00 };
  buf[1] = data;
  HAL_I2C_Master_Transmit(phi2c, lcd_i2c_addr, buf, 2, 100);
  HAL_Delay(1);
}

void lcd_init(I2C_HandleTypeDef *p_hi2c) {
  phi2c = p_hi2c;
  HAL_Delay(50);
  write_command(0x38);
  write_command(0x39);
  write_command(0x14);
  write_command(0x73);  // Contrast: C3=0 C2=0 C1=1 C0=1
  write_command(0x52);  // Contrast: BON=0 C5=1 C4=0
  write_command(0x6c);
  HAL_Delay(250);
  write_command(0x38);
  write_command(0x01);
  write_command(0x0c);
  HAL_Delay(50);
}

void lcd_clear(void) {
  write_command(0x01);
}

void lcd_newline(void) {
  write_command(0xc0);
}

void lcd_move_left(void) {
  write_command(0x10);
}

void lcd_move_right(void) {
  write_command(0x14);
}

void lcd_string(char *pbuf, uint8_t len) {
  uint8_t i;
  for(i=0; i<len; i++) {
    write_data((uint8_t)pbuf[i]);
  }
}

void lcd_test(void) {
  write_data(0x33);  // 3
  write_data(0x37);  // 7
  write_data(0x2e);  // .
  write_data(0x30);  // 0
  write_data(0xf2);  // o
  write_data(0x43);  // C
  write_command(0xc0);  // new line
  write_data(0x28);  // (
  write_data(0x5e);  // ~
  write_data(0x2d);  // -
  write_data(0x5e);  // ~
  write_data(0x29);  // )
}
