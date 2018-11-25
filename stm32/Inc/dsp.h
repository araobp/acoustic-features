/*
 * dsp.h
 *
 *  Created on: 2018/10/16
 */

#ifndef DSP_H_
#define DSP_H_

#include "arm_math.h"

#define NN 512

// Pre-emphasis coefficient
#define ALPHA 0.97f

// The number of filters
// Note: NUM_FILTERS_L >= NUM_FILTERS
#define NUM_FILTERS_MEL 40     // Mel-spectrogram and MFCCs
#define NUM_FILTERS_SPEC 255  // Linear-spectrogram

// Adjust mel filterbank so that the output to uart does not become too small
#define ADJUST_MEL_FILTERBANK 2.0f

// Note: MFCC_STREAMING is tentative.
typedef enum {
  RAW_WAVE, FFT, SPECTROGRAM, MEL_SPECTROGRAM, MFCC, MFCC_STREAMING, FILTERBANK
} mode;

extern float32_t filterbank[NUM_FILTERS_SPEC+2][NN/8];

void init_dsp(float32_t sampling_frequency);

void generate_filters(mode mode);

float32_t log10_approx(float32_t x);

// DSP pipeline functions
void apply_pre_emphasis(float32_t *inout);
void apply_ac_coupling(float32_t *inout);
void apply_hann(float32_t *inout);
void apply_fft(float32_t *inout);
void apply_filterbank(float32_t *inout, mode mode);
void apply_psd_logscale(float32_t *inout);
void apply_dct2(float32_t *inout);

#endif /* DSP_H_ */
