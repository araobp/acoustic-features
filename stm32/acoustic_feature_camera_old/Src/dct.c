/*
 * dct.c
 *
 *  Created on: 2019/01/08
 *
 *  Discrete Cosine Transform
 *
 */

#include <stdlib.h>
#include "math.h"
#include "dct.h"

float32_t c_k(int k) {
  return (k == 0) ? 1.0 / sqrt(2.0) : 1.0;
}

/**
 * @brief  Initialization function for the DCT2.
 * @param[in]     *S         points to an instance of floating-point DCT2 structure.
 * @param[in]     width      length of the DCT2.
 * @return        none.
 */
void dct2_init_f32(dct2_instance_f32 *S, uint16_t width) {
  float32_t *pDataW = NULL;
  float32_t *pDataW_I = NULL;
  float32_t *pDataX = NULL;
  S->width = width;

  arm_mat_init_f32(&(S->Y), width, 1, NULL);

  pDataW = (float32_t *) (calloc(width * width, sizeof(float32_t)));
  arm_mat_init_f32(&(S->W), width, width, pDataW);

  pDataW_I = (float32_t *) (calloc(width * width, sizeof(float32_t)));
  arm_mat_init_f32(&(S->W_I), width, width, pDataW_I);

  pDataX = (float32_t *) (calloc(width, sizeof(float32_t)));
  arm_mat_init_f32(&(S->X), width, 1, pDataX);

  for (int k = 0; k < S->width; k++) {
    for (int n = 0; n < S->width; n++) {
      S->W.pData[k * S->width + n] = arm_cos_f32(
          (k * (2 * n + 1) * M_PI) / (2 * S->width));
    }
  }

  for (int n = 0; n < S->width; n++) {
    for (int k = 0; k < S->width; k++) {
      S->W_I.pData[n * S->width + k] = c_k(k)
          * arm_cos_f32((k * (2 * n + 1) * M_PI) / (2 * S->width));
    }
  }

}

/**
 * @brief  Initialization function for the DCT2 2D.
 * @param[in]     *S         points to an instance of floating-point DCT2 structure.
 * @param[in]     height     DCT2 2D width.
 * @param[in]     width      DCT2 2D height.
 * @return        none.
 */
void dct2_2d_init_f32(dct2_instance_f32 *S, uint16_t height, uint16_t width) {
  dct2_init_f32(S, width);
  S->height = height;
}

/**
 * @brief DCT Type-II. The definition is same as scipy.fftpack.dct's definition.
 * @param[in]     *S         points to an instance of floating-point DCT2 structure.
 * @param[in]     *pSrc      points to the input buffer.
 * @param[out]    *pDst      points to the output buffer.
 * @param[in]     idctFlag   DCT if flag is 0, IDCT if flag is 1.
 * @return        none.
 */
void dct2_f32(dct2_instance_f32 *S, float32_t *pSrc, float32_t *pDst,
    uint8_t idctFlag) {

  S->X.pData = pSrc;
  S->Y.pData = pDst;

  if (idctFlag == 0) {
    arm_mat_mult_f32(&(S->W), &(S->X), &(S->Y));
    pDst[0] = pDst[0] * c_k(0);
    arm_scale_f32(pDst, (float32_t) (sqrt(2.0 / S->width)), pDst, S->width);
  } else {
    arm_mat_mult_f32(&(S->W_I), &(S->X), &(S->Y));
    arm_scale_f32(pDst, (float32_t) (sqrt(2.0 / S->width)), pDst, S->width);
  }
}

/**
 * @brief DCT Type-II 2D. The definition is same as scipy.fftpack.dct's definition.
 * @param[in]     *S         points to an instance of floating-point DCT2 structure.
 * @param[in]     *pSrc      points to the input buffer.
 * @param[out]    *pDst      points to the output buffer.
 * @param[in]     idctFlag   DCT if flag is 0, IDCT if flag is 1.
 * @return        none.
 */
void dct2_2d_f32(dct2_instance_f32 *S, float32_t *pSrc, float32_t *pDst,
    uint8_t idctFlag) {

  arm_matrix_instance_f32 X;
  arm_matrix_instance_f32 Y;

  for (int j = 0; j < S->height; j++) {
    dct2_f32(S, pSrc + (j * S->width), pDst + (j * S->width), idctFlag);
  }
  arm_mat_init_f32(&X, S->height, S->width, pDst);
  arm_mat_init_f32(&Y, S->width, S->height, pSrc);
  arm_mat_trans_f32(&X, &Y);

  for (int j = 0; j < S->width; j++) {
    dct2_f32(S, pSrc + (j * S->height), pDst + (j * S->height), idctFlag);
  }
  arm_mat_init_f32(&X, S->width, S->height, pDst);
  arm_mat_init_f32(&Y, S->height, S->width, pSrc);
  arm_mat_trans_f32(&X, &Y);
  arm_copy_f32(pSrc, pDst, S->height*S->width);
}
