#ifndef __AI_H__
#define __AI_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stdint.h>
#include "ai_platform.h"
#include "dsp.h"
#include "lcd.h"
#include "i2c.h"

/**
 * Note on AI inference processing.
 *
 * Since the auto-generated "app_x-cube-ai.c" is not flexible enough,
 * I decided to implement common AI routines in "ai.h" and "ai.c".
 *
 * "ai.c" and "app_x-cube-ai.c" refer to the following global variables
 * define in "main.c":
 * - int8_t mfsc_buffer[NUM_FILTERS * 200];
 * - int8_t mfcc_buffer[NUM_FILTERS * 200];
 * - int pos;
 * - bool start_inference
 */
extern int8_t mfsc_buffer[NUM_FILTERS * 200];
#ifndef FEATURE_MFSC
extern int8_t mfcc_buffer[NUM_FILTERS * 200];
#endif
extern int pos;
extern bool start_inference;

/**
 * Enable/disable AI
 */
//#define INFERENCE

/**
 * Use case definition
 */
//#define MUSICAL_INSTRUMENT_RECOGNITION
//#define KEY_WORD_DETECTION
#define ENVIRONMENTAL_SOUND_CLASSIFICATION

// Activity detection in dB
#ifdef KEY_WORD_DETECTION
  #define ACTIVITY_THRESHOLD 5.0
#else
  #define ACTIVITY_THRESHOLD -30.0
#endif
#define ACTIVITY_OFFSET 5U

/**
 * Feature definition
 */
#define WINDOW_LENGTH 64U

/*
 * Moving average of inference results
 */
#define HISTORY_LENGTH 5U

/**
 * Beam forming
 */
#define DISABLE_BEAMFORMING

/*--- Function prototypes ---*/

int ai_init(void);
void ai_infer(ai_float *input_data, ai_float* output_data);

#ifdef __cplusplus
}
#endif

#endif /* __AI_H__ */
