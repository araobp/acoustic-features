/*
 * dsp.c
 *
 *  Created on: 2018/10/16
 *
 *  Reference:
 *  - https://haythamfayek.com/2016/04/21/speech-processing-for-machine-learning.html
 *  - https://www.utdallas.edu/ssprl/files/CNN-VAD-IEEE-Access.pdf
 */

#include <dsp.h>
#include "arm_math.h"
#include "math.h"
#include "arm_const_structs.h"
#include "main.h"

const float32_t RECIPROCAL_NN = 1.0 / (float32_t) NN;

float32_t fs = 0.0f;      // Sampling frequency
float32_t nyq_fs = 0.0f;  // Nyquist frequency

// RFFT and FIR instances
arm_rfft_fast_instance_f32 S;
arm_fir_instance_f32 S_PRE;
arm_fir_instance_f32 S_WPRE;
arm_rfft_fast_instance_f32 S_DCT;

// Pre-emphasis
float32_t fir_coefficients[2] = { -ALPHA, 1.0f };
float32_t fir_w_coefficients[2] = { -W_ALPHA, 1.0f };
float32_t state_buf[NN + 1] = { 0.0f };
float32_t state_w_buf[NN + 1] = { 0.0f };

// Mel filter bank
float32_t filterbank[NUM_FILTERS + 2][FILTER_LENGTH] = { { 0.0f } };
int k_range[NUM_FILTERS + 2][2] = { { 0 } };

// Half sample shifter for DCT2 calculation with RFFT
float32_t half_sample_shifter[NUM_FILTERS * 2] = { 0.0f };

// Hann window
float32_t hann_window[NN] = { 0.0f };

// Temporary buffer for signal processing
float32_t signal_buf[NN] = { 0.0f };

/*
 *  log10 approximation
 *
 *  reference: https://community.arm.com/tools/f/discussions/4292/cmsis-dsp-new-functionality-proposal
 */
const float32_t C[4] = { 1.23149591368684f, -4.11852516267426f,
    6.02197014179219f, -3.13396450166353f };
const float32_t LOG10_2 = log10(2.0f);
float32_t log10_approx(float32_t x) {
  float32_t f, l;
  int e;
  f = frexpf(fabsf(x), &e);
  l = LOG10_2 * (C[0] * f * f * f + C[1] * f * f + C[2] * f + C[3] + e);
  return l;
  //return (l >= 0.0) ? l : 0.0;  // regard a negative value as featureless
}

// Hann window generation
void hann(int num) {
  arm_fill_f32(0.0f, hann_window, NN);
  float32_t scale = 2.0f * PI / (float32_t) num;
  for (int n = 0; n < num; n++) {
    hann_window[n] = 0.5f - 0.5f * arm_cos_f32((float) n * scale);
  }
}

// Frequency in Hz to Mel-scale
float32_t freq2mel(float32_t hz) {
  return 2595.0f * log10(hz / 700.0f + 1.0f);
}

// Mel-scale to Frequency in Hz
float32_t mel2freq(float32_t mel) {
  return 700.0 * (pow(10.0, (mel / 2595.0f)) - 1.0f);
}

// Generate Mel filter bank
void generate_filters(void) {
  const float32_t mel_min = 0.0f;
  float32_t mel_points[NUM_FILTERS + 2];
  float32_t hz_points[NUM_FILTERS + 2];
  float32_t f[NUM_FILTERS + 2];
  float32_t f_minus, f_center, f_plus;
  float32_t mel_max = freq2mel(nyq_fs);
  float32_t delta_mel = (mel_max - mel_min) / (NUM_FILTERS + 2);
  for (int m = 0; m < NUM_FILTERS + 2; m++) {
    mel_points[m] = delta_mel * m;
    hz_points[m] = mel2freq(mel_points[m]);
    f[m] = floor((NN + 1) * hz_points[m] / fs);
  }
  for (int m = 1; m < NUM_FILTERS + 1; m++) {
    for (int k = 1; k < NN / 2; k++) {
      f_minus = f[m - 1];
      f_center = f[m];
      f_plus = f[m + 1];
      for (int k = f_minus; k < f_center; k++) {
        filterbank[m][k - (int) f_minus] = (k - f_minus) / (f_center - f_minus);
      }
      for (int k = f_center; k <= f_plus; k++) {
        filterbank[m][k - (int) f_minus] = (f_plus - k) / (f_plus - f_center);
      }
      k_range[m][0] = (int) f_minus;
      k_range[m][1] = (int) f_plus - (int) f_minus + 1;
    }
  }
}

// Generate half sample shifter for DCT2
void generate_half_sample_shifter(void) {
  int re, im;
  float32_t num_filters_2 = (float32_t) NUM_FILTERS * 2;
  for (int k = 0; k < NUM_FILTERS; k++) {
    re = k * 2;
    im = re + 1;
    half_sample_shifter[re] = arm_cos_f32(
        -1.0 * PI * (float32_t) k / num_filters_2);
    half_sample_shifter[im] = arm_sin_f32(
        -1.0 * PI * (float32_t) k / num_filters_2);
  }
}

/*
 * DSP pipeline initialization
 */
void init_dsp(float32_t f_s) {
  // Generate Hanning window
  hann(NN);
  fs = f_s;
  nyq_fs = f_s / 2.0;
  arm_rfft_fast_init_f32(&S, NN);
  arm_rfft_fast_init_f32(&S_DCT, NUM_FILTERS * 2);
  arm_fir_init_f32(&S_PRE, 2, fir_coefficients, state_buf, NN);
  arm_fir_init_f32(&S_WPRE, 2, fir_w_coefficients, state_w_buf, NN);
  generate_filters();
  generate_half_sample_shifter();
}

//--- DSP pipeline functions -----------------------------//

// Apply pre-emphasis
void apply_pre_emphasis(float32_t *signal) {
  arm_fir_f32(&S_PRE, signal, signal, NN);
}

void apply_weak_pre_emphasis(float32_t *signal) {
  arm_fir_f32(&S_WPRE, signal, signal, NN);
}

// AC coupling (to remove DC)
void apply_ac_coupling(float32_t *signal) {
  float32_t mean;
  static float32_t mean_hist[NUM_MEANS] = { 0.0f };
  arm_copy_f32(mean_hist + 1, mean_hist, NUM_MEANS - 1);
  arm_mean_f32(signal, NN, mean_hist + NUM_MEANS - 1);
  arm_mean_f32(signal, NUM_MEANS, &mean);
  arm_offset_f32(signal, -mean, signal, NN);
}

// Apply Hann window
void apply_hann(float32_t *signal) {
  arm_mult_f32(signal, hann_window, signal, NN);
}

// FFT
void apply_fft(float32_t *signal) {
  // Caution: arm_rfft_fast_f32() rewrites the 2nd arg (signal)
  arm_rfft_fast_f32(&S, signal, signal_buf, 0);
  arm_copy_f32(signal_buf, signal, NN);
}

// PSD
void apply_psd(float32_t *signal) {
  arm_cmplx_mag_f32(signal, signal_buf, NN / 2);
  arm_scale_f32(signal_buf, RECIPROCAL_NN, signal, NN / 2);
}

// PSD in logscale
void apply_psd_logscale(float32_t *signal) {
  for (int n = 0; n < NN / 2; n++) {
    signal[n] = 20.0 * log10_approx(signal[n]);
  }
}

// Apply mel filter bank
void apply_filterbank(float32_t *signal) {
  float32_t sum = 0.0f;
  int left_k, len;
  arm_fill_f32(0.0f, signal_buf, NN / 2);
  for (int m = 1; m < NUM_FILTERS + 1; m++) {
    left_k = k_range[m][0];
    len = k_range[m][1];
    arm_dot_prod_f32(&signal[left_k], filterbank[m], len, &sum);
    signal_buf[m - 1] = sum;
  }
  arm_copy_f32(signal_buf, signal, NUM_FILTERS);
}

// Filtered PSD in logscale
void apply_filterbank_logscale(float32_t *signal) {
  for (int n = 0; n < NUM_FILTERS; n++) {
    signal[n] = 20.0 * log10_approx(signal[n]);
  }
}

// DCT Type-II
void apply_dct2(float32_t *signal) {
  float32_t out[NUM_FILTERS * 2] = { 0.0f };
  arm_copy_f32(signal, signal_buf, NUM_FILTERS);
  for (int n = 0; n < NUM_FILTERS; n++) {
    signal_buf[NUM_FILTERS + n] = signal[NUM_FILTERS - n - 1];
  }
  arm_rfft_fast_f32(&S_DCT, signal_buf, out, 0);
  arm_cmplx_mult_cmplx_f32(out, half_sample_shifter, out, NUM_FILTERS);
  for (int n = 0; n < NUM_FILTERS; n++) {
    signal[n] = out[n * 2] * ADJUST_MFCCS;
  }
}
