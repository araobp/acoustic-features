/*
 * dct.h
 *
 *  Created on: 2019/01/08
 */

#ifndef DCT_H_
#define DCT_H_

#include "stdbool.h"
#include "arm_math.h"

/**
 * DCT Type-II instance
 *
 * Y = W * X;
 */
typedef struct {
  uint16_t width;
  uint16_t height;
  arm_matrix_instance_f32 Y;
  arm_matrix_instance_f32 W;
  arm_matrix_instance_f32 W_I;
  arm_matrix_instance_f32 X;
} dct2_instance_f32;

void dct2_init_f32(dct2_instance_f32 *S, uint16_t width);

void dct2_f32(dct2_instance_f32 *S, float32_t *pSrc, float32_t *pDst, uint8_t idctFlag);

void dct2_2d_init_f32(dct2_instance_f32 *S, uint16_t height, uint16_t width);

void dct2_2d_f32(dct2_instance_f32 *S, float32_t *pSrc, float32_t *pDst,
    uint8_t idctFlag);

#endif /* DCT_H_ */
