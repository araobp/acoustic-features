/*
 * rn4020.h
 *
 *  Created on: 2019/04/25
 */

#ifndef RN4020_H_
#define RN4020_H_

#include <stdint.h>
#include "usart.h"

#define NOTIFY_COMMAND "SUW,010203040506070809000A0B0C0D0E0F,"

void sendData(uint8_t *data, int len);

#endif /* RN4020_H_ */
