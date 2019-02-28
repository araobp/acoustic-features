#ifndef __AI_H__
#define __AI_H__

#include <stdint.h>
#include "ai_platform.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Note on AI inference processing.
 *
 * Since the auto-generated "app_x-cube-ai.c" is not flexible enough,
 * I decided to implement common AI routines in "ai.h" and "ai.c".
 *
 * "ai.c" and "app_x-cube-ai.c" refer to the following global variables
 * define in "main.h" and "main.c":
 * - int8_t mfsc_buffer[NUM_FILTERS * 200];
 * - int8_t mfcc_buffer[NUM_FILTERS * 200];
 * - int32_t mfsc_power[200];
 * - int pos;
 */

/**
 * Acoustic event detection use cases
 */
//#define MUSICAL_INSTRUMENT_RECOGNITION
//#define KEY_WORD_DETECTION
#define ENVIRONMENTAL_SOUND_CLASSIFICATION

bool voice_active(int length, int32_t threshold);

int ai_init(void);
void ai_infer(ai_float *input_data, ai_float* output_data);

#ifdef __cplusplus
}
#endif

#endif /* __AI_H__ */
