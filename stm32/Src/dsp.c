/*
 * dsp.c
 *
 *  Created on: 2018/10/16
 */

#include <dsp.h>
#include "arm_math.h"
#include "math.h"
#include "arm_const_structs.h"
#include "main.h"

const float32_t RECIPROCAL_NN = 1.0/(float32_t)NN;

float32_t fs = 0.0f;
float32_t nyq_fs = 0.0f;

arm_rfft_fast_instance_f32 S;
arm_fir_instance_f32 S_PRE;
arm_rfft_fast_instance_f32 S_DCT;

float32_t filterbank[NUM_FILTERS_SPEC+2][NN/8] = { { 0.0f } };

float32_t hz_freqs[NUM_FILTERS_SPEC+2] = { 0.0f };
uint32_t hz_freqs_n[NUM_FILTERS_SPEC+2] = { 0.0f };

float32_t hann_window[NN] = { 0.0f };

float32_t signal_buf[NN] = { 0.0f };

// pre-emphasis
float32_t fir_coefficients[2] = {-ALPHA, 1.0f};
float32_t state_buf[NN+1] = { 0.0f };

// Half sample shifter
float32_t half_sample_shifter[NUM_FILTERS_MEL * 2] = { 0.0f };

// hann window generation
void hann(int num) {
  arm_fill_f32(0.0f, hann_window, NN);
  float32_t scale = 2.0f * PI / (float32_t) num;
  for (int n = 0; n < num; n++) {
    hann_window[n] = 0.5f - 0.5f * arm_cos_f32((float) n * scale);
  }
}

/*
 *  log10 approximation
 *
 *  reference: https://community.arm.com/tools/f/discussions/4292/cmsis-dsp-new-functionality-proposal
 */
const float32_t C[4] = {1.23149591368684f, -4.11852516267426f, 6.02197014179219f, -3.13396450166353f};
const float32_t LOG10_2 = log10(2.0f);
float32_t log10_approx(float32_t x) {
  float32_t f, l;
  int e;
  f = frexpf(fabsf(x), &e);
  l = LOG10_2 * (C[0]*f*f*f + C[1]*f*f + C[2]*f + C[3] + e);
  return (l > 0.000001) ? l : 0.000001;  // for numerical stability
}

// Frequency in Hz to Mel-scale
float32_t hz2mel(float32_t hz) {
  return 2595.0f * log10(hz/700.0f + 1.0f);
}

// Mel-scale to Frequency in Hz
float32_t mel2hz(float32_t mel) {
  return 700.0 * (pow(10.0, (mel/2595.0f)) - 1.0f);
}

float32_t n2hz(uint32_t n) {
  return (float32_t)n/(float32_t)NN * nyq_fs;
}

void clear_filterbank(void) {
  for (int m = 0; m < NUM_FILTERS_SPEC + 2; m++) {
    for (int n = 0; n < NN/8; n++) {
      filterbank[m][n] = 0.0f;
    }
    hz_freqs[m] = 0.0f;
    hz_freqs_n[m] = 0;
  }
}

/*
 * Filter bank: Mel scale
 */
void generate_mel_scale_filters(void) {
  int left_n, center_n, right_n;
  float32_t freq_m_minus_1, freq_m, freq_m_plus_1;
  float32_t mel_freq_high;
  float32_t mel_delta;
  float32_t divider;

  clear_filterbank();
  mel_freq_high = hz2mel(nyq_fs);
  mel_delta = mel_freq_high/(float32_t)(NUM_FILTERS_MEL + 2);

  for (int m = 0; m < NUM_FILTERS_MEL + 2; m++) {
    hz_freqs[m] = mel2hz(mel_delta * m);
    hz_freqs_n[m] = (uint32_t)(hz_freqs[m] / nyq_fs * NN / 2);
  }
  for (int m = 1; m < NUM_FILTERS_MEL + 1; m++) {
    left_n = hz_freqs_n[m-1];
    center_n = hz_freqs_n[m];
    right_n = hz_freqs_n[m+1];

    freq_m_minus_1 = n2hz(left_n);
    freq_m = n2hz(center_n);
    freq_m_plus_1 = n2hz(right_n);
    divider = (float32_t)(right_n - left_n) / ADJUST_MEL_FILTERBANK;

    for (int n = left_n; n < center_n; n++) {
      filterbank[m][n - left_n] = (n2hz(n) - freq_m_minus_1)/(freq_m - freq_m_minus_1)/divider;
    }

    filterbank[m][center_n - left_n] = 1.0f/divider;

    for (int n= center_n + 1; n <= right_n; n++) {
      filterbank[m][n - left_n] = (freq_m_plus_1 - n2hz(n))/(freq_m_plus_1 - freq_m)/divider;
    }
  }
}

/*
 * Filter bank: linear scale
 */
void generate_linear_scale_filters(void) {
  int left_n, center_n, right_n;
  float32_t freq_m_minus_1, freq_m, freq_m_plus_1;
  float32_t freq_high;
  float32_t delta;

  clear_filterbank();
  freq_high = (float32_t)fs/2.0;
  delta = freq_high/(float32_t)(NUM_FILTERS_SPEC + 2);

  for (int m = 0; m < NUM_FILTERS_SPEC + 2; m++) {
    hz_freqs[m] = delta * m;
    hz_freqs_n[m] = (uint32_t)(hz_freqs[m] / nyq_fs * NN / 2);
  }
  for (int m = 1; m < NUM_FILTERS_SPEC + 1; m++) {
    left_n = hz_freqs_n[m-1];
    center_n = hz_freqs_n[m];
    right_n = hz_freqs_n[m+1];

    freq_m_minus_1 = n2hz(left_n);
    freq_m = n2hz(center_n);
    freq_m_plus_1 = n2hz(right_n);

    for (int n = left_n; n < center_n; n++) {
      filterbank[m][n - left_n] = (n2hz(n) - freq_m_minus_1)/(freq_m - freq_m_minus_1);
    }

    filterbank[m][center_n - left_n] = 1.0f;

    for (int n= center_n + 1; n <= right_n; n++) {
      filterbank[m][n - left_n] = (freq_m_plus_1 - n2hz(n))/(freq_m_plus_1 - freq_m);
    }
  }
}

void generate_filters(mode mode) {
  if (mode == MEL_SPECTROGRAM) {
    generate_mel_scale_filters();
  } else if (mode == SPECTROGRAM) {
    generate_linear_scale_filters();
  }
}

void generate_half_sample_shifter(void) {
  int re, im;
  float32_t num_filters_2 = (float32_t)NUM_FILTERS_MEL * 2;
  for (int k = 0; k < NUM_FILTERS_MEL; k ++) {
    re = k * 2;
    im = re + 1;
    half_sample_shifter[re] = arm_cos_f32(-1.0*PI*(float32_t)k/num_filters_2);
    half_sample_shifter[im] = arm_sin_f32(-1.0*PI*(float32_t)k/num_filters_2);
  }
}

/*
 * dsp initialization
 */
void init_dsp(float32_t f_s) {
  // Generate Hanning window
  hann(NN);
  fs = f_s;
  nyq_fs = f_s/2.0;
  arm_rfft_fast_init_f32(&S, NN);
  arm_rfft_fast_init_f32(&S_DCT, NUM_FILTERS_MEL*2);
  arm_fir_init_f32(&S_PRE, 2, fir_coefficients, state_buf, NN+1);
  generate_mel_scale_filters();
  //generate_linear_scale_filters();
  generate_half_sample_shifter();
}

//--- DSP pipeline functions -----------------------------//

void apply_pre_emphasis(float32_t *inout) {
  arm_fir_f32(&S_PRE, inout, inout, NN);
}

void apply_ac_coupling(float32_t *inout) {
  float32_t mean;
  arm_mean_f32(inout, NN, &mean);
  arm_offset_f32(inout, -mean, inout, NN);
}

void apply_hann(float32_t *inout) {
  arm_mult_f32(inout, hann_window, inout, NN);
}

void apply_fft(float32_t *inout) {
  arm_rfft_fast_f32(&S, inout, signal_buf, 0);
  arm_copy_f32(signal_buf, inout, NN);
}

void apply_filterbank(float32_t *inout, mode mode) {
  float32_t sum = 0.0f;
  int left_n, right_n, len, num_filters;

  if (mode == SPECTROGRAM) {
    num_filters = NUM_FILTERS_SPEC;
  } else {
    num_filters = NUM_FILTERS_MEL;
  }

  arm_fill_f32(0.0f, signal_buf, NN/2);
  for (int m = 1; m < num_filters + 1; m++) {
    left_n = hz_freqs_n[m-1];
    right_n = hz_freqs_n[m+1];
    len = right_n - left_n + 1;
    arm_dot_prod_f32(&inout[left_n], filterbank[m], len, &sum);
    signal_buf[m-1] = sum;
  }
  arm_copy_f32(signal_buf, inout, num_filters);
}

void apply_psd_logscale(float32_t *inout) {
  arm_cmplx_mag_f32(inout, signal_buf, NN / 2);
  arm_scale_f32(inout, RECIPROCAL_NN, inout, NN / 2);
  for (int n = 0; n < NN / 2; n++) {
    inout[n] = 20.0 * log10_approx(signal_buf[n]);
  }
}

void apply_dct2(float32_t *inout) {
  float32_t in[NUM_FILTERS_MEL*2] = { 0.0f };
  float32_t out[NUM_FILTERS_MEL*2] = { 0.0f };
  arm_copy_f32(inout, in, NUM_FILTERS_MEL);
  for (int n = 0; n < NUM_FILTERS_MEL; n++) {
    in[n+NUM_FILTERS_MEL] = in[NUM_FILTERS_MEL-n-1];
  }
  arm_rfft_fast_f32(&S_DCT, in, out, 0);
  arm_scale_f32 (out, 2.0, out, NUM_FILTERS_MEL*2);
  arm_cmplx_mult_cmplx_f32(out, half_sample_shifter, out, NUM_FILTERS_MEL);
  for (int n = 0; n < NUM_FILTERS_MEL; n++) {
    inout[n] = out[n*2];
  }
}
