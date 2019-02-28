/*
 * dsp.h
 *
 *  Created on: 2018/10/16
 */

#ifndef DSP_H_
#define DSP_H_

#include "arm_math.h"
#include "stdbool.h"

// The number of samples per frame
#define NN 512

// Pre-emphasis coefficient
#define ALPHA 0.95f
#define W_ALPHA 0.7f  // Weak pre-emphasis

// The number of filters
#define NUM_FILTERS 40U
#define FEATURE_MFSC
//#define FEATURE_MFCC
//#define CUTOFF 13U
#define WINDOW_LENGTH 64

// Note: FEATURES includes both MFSCs and MFCCs
typedef enum {
  NONE, RAW_WAVE, FFT, SPECTROGRAM, FEATURES
} mode;

// The number of values in the mean value history for AC coupling
#define NUM_MEANS 16U

// Length of each filter in the filter bank
// Note: this is just to save RAM
#define FILTER_LENGTH 32

// Filter bank
// Note: "+2" means both edges, i.e., zero and the max number
extern float32_t filterbank[NUM_FILTERS+2][FILTER_LENGTH];
int k_range[NUM_FILTERS+2][2];

// Disable beam forming
#define DISABLE_BEAMFORMING

//----- Function declarations -----------------------------------//

// DSP pipeline initialization
void init_dsp(float32_t sampling_frequency);

// DSP pipeline functions
void apply_pre_emphasis(float32_t *signal);
void apply_weak_pre_emphasis(float32_t *signal);
void apply_ac_coupling(float32_t *signal);
void apply_hann(float32_t *signal);
void apply_fft(float32_t *signal);
void apply_psd(float32_t *signal);
void apply_psd_logscale(float32_t *signal);
void apply_filterbank(float32_t *signal);
void apply_filterbank_logscale(float32_t *signal);
void apply_dct2(float32_t *signal);

#endif /* DSP_H_ */
