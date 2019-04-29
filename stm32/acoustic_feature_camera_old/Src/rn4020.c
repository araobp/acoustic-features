/*
 * rn4020.c
 *
 *  Created on: 2019/04/25
 */

#include "rn4020.h"
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

char send_buf[100];

/**
 * Send byte array (max. 20 bytes) to a BLE central via RN4020 module
 */
void sendData(uint8_t *data, int len) {
  char ascii_hex_buf[2];

  strcpy(send_buf, NOTIFY_COMMAND);
  for (int i = 0; i < len; i++) {
    sprintf(ascii_hex_buf, "%02x", data[i]);
    send_buf[37+i*2] = ascii_hex_buf[0];
    send_buf[37+i*2+1] = ascii_hex_buf[1];
  }
  send_buf[37+len*2] = '\n';

  HAL_UART_Transmit(&huart1, (uint8_t *)send_buf, 37+len*2+1, 0xffff);
}
