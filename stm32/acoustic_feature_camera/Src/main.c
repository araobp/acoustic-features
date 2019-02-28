/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 ** This notice applies to any and all portions of this file
 * that are not between comment pairs USER CODE BEGIN and
 * USER CODE END. Other portions of this file, whether
 * inserted by the user or by software development tools
 * are owned by their respective copyright owners.
 *
 * COPYRIGHT(c) 2018 STMicroelectronics
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *   1. Redistributions of source code must retain the above copyright notice,
 *      this list of conditions and the following disclaimer.
 *   2. Redistributions in binary form must reproduce the above copyright notice,
 *      this list of conditions and the following disclaimer in the documentation
 *      and/or other materials provided with the distribution.
 *   3. Neither the name of STMicroelectronics nor the names of its contributors
 *      may be used to endorse or promote products derived from this software
 *      without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 ******************************************************************************
 */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "crc.h"
#include "dac.h"
#include "dfsdm.h"
#include "dma.h"
#include "i2c.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"
#include "app_x-cube-ai.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "stdbool.h"
#include "arm_math.h"
#include "math.h"
#include "stdio.h"
#include "dsp.h"
#include "string.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

// N / 2
const int NN_HALF = NN / 2;

// N * 2
const int NN_DOUBLE = NN * 2;

// flag: "new PCM data has just been copied to buf"
volatile bool new_pcm_data_l_a = false;
volatile bool new_pcm_data_l_b = false;
volatile bool new_pcm_data_r_a = false;
volatile bool new_pcm_data_r_b = false;

// output trigger
volatile bool printing = false;

// UART output mode
volatile mode output_mode = FEATURES;
mode filter_type = FEATURES;  // Current filter bank

// UART one-byte input buffer
uint8_t rxbuf[1];

// Pre-emphasis toggle
volatile bool pre_emphasis_enabled = true;

// Beam forming setting
volatile angle_setting angle = CENTER;  // center
volatile beam_forming_setting beam_forming_mode = ENDFIRE;

// Debug
volatile debug debug_output = ELAPSED_TIME;
uint32_t elapsed_time = 0;

// Buffers
// Note: these variables are declared as "extern(al)".
int8_t mfsc_buffer[NUM_FILTERS * 200] = { 0.0f };
int8_t mfcc_buffer[NUM_FILTERS * 200] = { 0.0f };
int32_t mfsc_power[200] = { 0 };
int pos = 0;

/* Private variables ---------------------------------------------------------*/

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
/* Private function prototypes -----------------------------------------------*/

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

#ifndef INFERENCE
/*
 * Output raw wave or feature to UART by memory-to-peripheral DMA
 */
bool uart_tx(float32_t *in, mode mode, bool dma_start) {

  bool printing;
  int a, b;
  int c;
  static int cnt = 0;
  static int length = 0;
  static int idx = 0;

  static char uart_buf[NUM_FILTERS * 200 * 2] = { 0 };

  if (cnt == 0) {
    idx = 0;

    switch (mode) {

    case RAW_WAVE:
      length = NN;
      cnt = 1;
      break;

    case FFT:
      length = NN / 2;
      cnt = 1;
      break;

    case SPECTROGRAM:
      length = NN / 2;
      cnt = 200;
      break;

    case FEATURES:
      break;

    default:
      length = 0;
      break;

    }
  }

  // Quantization: convert float into int
  if (mode == RAW_WAVE) {
    for (int n = 0; n < length; n++) {
      uart_buf[idx++] = (uint8_t) (((int16_t) in[n]) >> 8);      // MSB
      uart_buf[idx++] = (uint8_t) (((int16_t) in[n] & 0x00ff));  // LSB
    }
  } else if (mode == FEATURES) {
    a = pos * NUM_FILTERS;
    b = (200 - pos) * NUM_FILTERS;
    c = 200 * NUM_FILTERS;
    // Time series order
    memcpy(uart_buf + b, mfsc_buffer, a);
    memcpy(uart_buf, mfsc_buffer + a, b);
    memcpy(uart_buf + b + c, mfcc_buffer, a);
    memcpy(uart_buf + c, mfcc_buffer + a, b);
  } else {
    for (int n = 0; n < length; n++) {
      if (in[n] < -128.0f) in[n] = -128.0f;
      uart_buf[idx++] = (int8_t) in[n];
    }
  }

  // memory-to-peripheral DMA to UART
  if (mode == FEATURES) {
    HAL_UART_Transmit_DMA(&huart2, (uint8_t *) uart_buf, NUM_FILTERS * 200 * 2);
    printing = false;
  } else if (--cnt == 0) {
    HAL_UART_Transmit_DMA(&huart2, (uint8_t *) uart_buf, idx);
    printing = false;
  } else if (dma_start) {
    HAL_UART_Transmit_DMA(&huart2, (uint8_t *) uart_buf, idx);
    idx = 0;
    printing = true;
  } else {
    printing = true;
  }

  return printing;
}
#endif

/*
 * DSP pipeline
 */
void dsp(float32_t *s1, mode mode) {

  uint32_t start = 0;
  uint32_t end = 0;

  start = HAL_GetTick();

  apply_ac_coupling(s1);  // remove DC

  if (mode >= FFT) {
    apply_hann(s1);
    apply_fft(s1);
    apply_psd(s1);
    if (mode < FEATURES) {
      apply_psd_logscale(s1);
    } else {
      apply_filterbank(s1);
      apply_filterbank_logscale(s1);
      mfsc_power[pos] = 0;
      for (int i = 0; i < NUM_FILTERS; i++) {
        mfsc_buffer[pos * NUM_FILTERS + i] = (int8_t) s1[i];
        mfsc_power[pos] += (int32_t)s1;
      }
      apply_dct2(s1);
      for (int i = 0; i < NUM_FILTERS; i++) {
        mfcc_buffer[pos * NUM_FILTERS + i] = (int8_t) s1[i];
      }
    }
  }
  if (++pos >= 200)
    pos = 0;

  end = HAL_GetTick();
  elapsed_time = end - start;
}

/*
 * Overlap dsp for spectrogram calculation
 *
 * 26.3msec          13.2msec stride
 * --- overlap dsp -------------
 * [b0|a0]            a(1/2) ... 13.2msec
 *    [a0|a1]         a(2/2) ... 13.2msec
 * --- overlap dsp -------------
 *       [a1|b0]      b(1/2) ... 13.2msec
 *          [b0|b1]   b(2/2) ... 13.2msec
 * --- overlap dsp -------------
 *             :
 */
void overlap_dsp(float32_t *buf, mode mode) {

  float32_t signal[NN] = { 0.0f };

  arm_copy_f32(buf, signal, NN);
  dsp(signal, mode);  // (1/2)
#ifndef INFERENCE
  if (printing) {
    printing = uart_tx(signal, mode, false);  // false: UART output pending
  }
#endif

  arm_copy_f32(buf + NN_HALF, signal, NN);
  dsp(signal, mode);  // (2/2)
#ifndef INFERENCE
  if (printing) {
    printing = uart_tx(signal, mode, true);  // true: UART output
  }
#endif
}

/*
 * Dump debug info
 */
void dump(void) {
  if (debug_output != DISABLED) {
    switch (debug_output) {
    case FILTERBANK:
      for (int m = 0; m < NUM_FILTERS + 2; m++) {
        printf("%d:%d,", k_range[m][0], k_range[m][1]);
        for (int n = 0; n < FILTER_LENGTH; n++) {
          printf("%.3f,", filterbank[m][n]);
        }
        printf("\n");
      }
      printf("e\n");
      break;
    case ELAPSED_TIME:
      printf("mode: %d, elapsed_time: %lu(msec)\n", output_mode, elapsed_time);
      break;
    default:
      break;
    }
    debug_output = DISABLED;
  }
}

/*
 * Apply beam forming
 */
void beam_forming(float32_t *signal, int32_t *l, int32_t *r,
    beam_forming_setting mode, int direction) {

  switch (mode) {
  case BROADSIDE:
    for (uint32_t n = 0; n < NN; n++) {
      signal[n] = (float32_t) (l[n + direction] >> 9)
          + (float32_t) (r[n + 2] >> 9);
    }
    break;
  case ENDFIRE:
    if (direction != 2) {
      for (uint32_t n = 0; n < NN; n++) {
        signal[n] = (float32_t) (l[n + 2] >> 9)
            - (float32_t) (r[n + direction] >> 9);
      }
    } else {  // Synchronous addition of data from two microphones
      for (uint32_t n = 0; n < NN; n++) {
        signal[n] = (float32_t) (l[n + 2] >> 9) + (float32_t) (r[n + 2] >> 9);
      }
    }
    break;
  case LEFT_MIC_ONLY:
    for (uint32_t n = 0; n < NN; n++) {
      signal[n] = (float32_t) (l[n + 2] >> 9);
    }
    break;
  case RIGHT_MIC_ONLY:
    for (uint32_t n = 0; n < NN; n++) {
      signal[n] = (float32_t) (r[n + 2] >> 9);
    }
    break;
  }

}

/*
 * Apply pre emphasis
 */
void pre_emphasis(float32_t *signal, int direction) {
  if (pre_emphasis_enabled) {
    if (beam_forming_mode == ENDFIRE && direction != 2) {
      apply_weak_pre_emphasis(signal);
    } else {
      apply_pre_emphasis(signal);
    }
  }
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  // Audio sample rate and period
  float32_t f_s;

  // DMA peripheral-to-memory double buffer
  int32_t input_buf_r[NN * 2 + 5] = { 0 };
  int32_t input_buf_l[NN * 2 + 5] = { 0 };

  // DMA memory-to-peripheral double buffer
  volatile uint16_t dac_out_buf_a[NN * 2] = { 0 };
  volatile uint16_t dac_out_buf_b[NN * 2] = { 0 };

  // PCM data store for further processing (FFT etc)
  float32_t signal_buf[NN + NN / 2] = { 0.0f };  // NN/2 overlap

  // n + NN
  int n_nn = 0;

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */
  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_DAC1_Init();
  MX_TIM6_Init();
  MX_DFSDM1_Init();
  MX_CRC_Init();
  MX_I2C1_Init();
  MX_X_CUBE_AI_Init();
  /* USER CODE BEGIN 2 */

  f_s = SystemCoreClock / hdfsdm1_channel2.Init.OutputClock.Divider
      / hdfsdm1_filter0.Init.FilterParam.Oversampling
      / hdfsdm1_filter0.Init.FilterParam.IntOversampling;

  // DSP initialization
  init_dsp(f_s);

  // Start timer 6 and DAC for DMA
  HAL_TIM_Base_Start(&htim6);
  HAL_DAC_Start(&hdac1, DAC_CHANNEL_1);
  HAL_DAC_Start_DMA(&hdac1, DAC_CHANNEL_1, (uint32_t*) dac_out_buf_a, NN * 2,
  DAC_ALIGN_12B_R);
  HAL_DAC_Start(&hdac1, DAC_CHANNEL_2);
  HAL_DAC_Start_DMA(&hdac1, DAC_CHANNEL_2, (uint32_t*) dac_out_buf_b, NN * 2,
  DAC_ALIGN_12B_R);

  HAL_Delay(1);

  // Enable DMA from DFSDM to buf (peripheral to memory)
  // Note: filter1 for left channel is started after filter 0 for right channel
  if (HAL_DFSDM_FilterRegularStart_DMA(&hdfsdm1_filter0, input_buf_r + 5,
  NN * 2) != HAL_OK) {
    Error_Handler();
  }
  if (HAL_DFSDM_FilterRegularStart_DMA(&hdfsdm1_filter1, input_buf_l + 5,
  NN * 2) != HAL_OK) {
    Error_Handler();
  }

  // Enable UART receive interrupt to receive a command
  // from an application processor
  HAL_UART_Receive_IT(&huart2, rxbuf, 1);

#ifdef DISABLE_BEAMFORMING
  beam_forming_mode = RIGHT_MIC_ONLY;
#endif
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1) {
    // Wait for next PCM samples from M1
    if (new_pcm_data_l_a) {  // 1st half of the buffer

      // Overlap
      arm_copy_f32(signal_buf + NN, signal_buf, NN_HALF);

      // Beam forming
      beam_forming(signal_buf + NN_HALF, input_buf_l, input_buf_r,
          beam_forming_mode, angle);

      // Pre-emphasis
      pre_emphasis(signal_buf + NN_HALF, angle);

      // Overlap dsp
      overlap_dsp(signal_buf, output_mode);

      // Output PCM data to DAC
      // Note: the signal after dsp for ML should be something like artificial.
      // Move the following code before dsp, if you want to monitor natural sound.
      for (uint32_t n = 0; n < NN; n++) {
        dac_out_buf_a[n] = (uint16_t) (((int32_t) signal_buf[n] >> 4) + 2048); // 12bit quantization
        dac_out_buf_b[n] = dac_out_buf_a[n];
      }

      new_pcm_data_l_a = false;

    }

    if (new_pcm_data_l_b) {  // 2nd half of the buffer

      // Buffering PCM data for beam forming: n=2 is center
      for (int n = 0; n < 5; n++) {
        input_buf_l[n] = input_buf_l[NN_DOUBLE + n];
        input_buf_r[n] = input_buf_r[NN_DOUBLE + n];
      }

      // Overlap
      arm_copy_f32(signal_buf + NN, signal_buf, NN_HALF);

      // Beam forming
      beam_forming(signal_buf + NN_HALF, input_buf_l + NN, input_buf_r + NN,
          beam_forming_mode, angle);

      // Pre-emphasis
      pre_emphasis(signal_buf + NN_HALF, angle);

      // Overlap dsp
      overlap_dsp(signal_buf, output_mode);

      // Output PCM data to DAC
      for (uint32_t n = 0; n < NN; n++) {
        n_nn = n + NN;
        dac_out_buf_a[n_nn] =
            (uint16_t) (((int32_t) signal_buf[n] >> 4) + 2048); // 12bit quantization
        dac_out_buf_b[n_nn] = dac_out_buf_a[n_nn];
      }

      new_pcm_data_l_b = false;
    }

    // Dump debug info
    dump();

    /* USER CODE END WHILE */

  MX_X_CUBE_AI_Process();
    /* USER CODE BEGIN 3 */

  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /**Initializes the CPU, AHB and APB busses clocks 
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 1;
  RCC_OscInitStruct.PLL.PLLN = 10;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV7;
  RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV2;
  RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /**Initializes the CPU, AHB and APB busses clocks 
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_4) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USART2|RCC_PERIPHCLK_I2C1
                              |RCC_PERIPHCLK_DFSDM1;
  PeriphClkInit.Usart2ClockSelection = RCC_USART2CLKSOURCE_PCLK1;
  PeriphClkInit.I2c1ClockSelection = RCC_I2C1CLKSOURCE_PCLK1;
  PeriphClkInit.Dfsdm1ClockSelection = RCC_DFSDM1CLKSOURCE_PCLK;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
  /**Configure the main internal regulator output voltage 
  */
  if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */
/**
 * @brief  Half regular conversion complete callback.
 * @param  hdfsdm_filter DFSDM filter handle.
 * @retval None
 */
void HAL_DFSDM_FilterRegConvHalfCpltCallback(
    DFSDM_Filter_HandleTypeDef *hdfsdm_filter) {
  if (!new_pcm_data_l_a && (hdfsdm_filter == &hdfsdm1_filter0)) {
    new_pcm_data_l_a = true;  // ready for 1st half of the buffer
  }
  if (!new_pcm_data_r_a && (hdfsdm_filter == &hdfsdm1_filter1)) {
    //new_pcm_data_r_a = true;
  }
}

/**
 * @brief  Regular conversion complete callback.
 * @note   In interrupt mode, user has to read conversion value in this function
 using HAL_DFSDM_FilterGetRegularValue.
 * @param  hdfsdm_filter : DFSDM filter handle.
 * @retval None
 */
void HAL_DFSDM_FilterRegConvCpltCallback(
    DFSDM_Filter_HandleTypeDef *hdfsdm_filter) {
  if (!new_pcm_data_l_b && (hdfsdm_filter == &hdfsdm1_filter0)) {
    new_pcm_data_l_b = true;  // ready for 2nd half of the buffer
  }
  if (!new_pcm_data_r_b && (hdfsdm_filter == &hdfsdm1_filter1)) {
    //new_pcm_data_r_b = true;
  }
}

/**
 * @brief  Retargets the C library printf function to the USART.
 * @param  None
 * @retval None
 */
int _write(int file, char *ptr, int len) {
  HAL_UART_Transmit(&huart2, (uint8_t *) ptr, (uint16_t) len, 0xFFFFFFFF);
  return len;
}

//  (This func is commented out: for a debug purpose only)
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
  if (GPIO_Pin == GPIO_PIN_13) {  // User button (blue tactile switch)
    //
  }
}

/*
 * One-byte command reception from an application processor
 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
  char cmd;

  cmd = rxbuf[0];

  switch (cmd) {

  // Pre-emphasis
  case 'P':
    pre_emphasis_enabled = true;
    break;
  case 'p':
    pre_emphasis_enabled = false;
    break;

    // Beam forming
  case 'L':
    angle = LEFT2;
    break;
  case 'l':
    angle = LEFT;
    break;
  case 'c':
    angle = CENTER;
    break;
  case 'r':
    angle = RIGHT;
    break;
  case 'R':
    angle = RIGHT2;
    break;
  case 'b':
    beam_forming_mode = BROADSIDE;
    break;
  case 'e':
    beam_forming_mode = ENDFIRE;
    break;
  case '[':
    beam_forming_mode = LEFT_MIC_ONLY;
    break;
  case ']':
    beam_forming_mode = RIGHT_MIC_ONLY;
    break;
  case 'f':
    debug_output = FILTERBANK;
    break;
  case 't':
    debug_output = ELAPSED_TIME;
    break;
    // The others
  default:
    output_mode = (mode) (cmd - 0x30);
    printing = true;
    break;
  }

  HAL_UART_Receive_IT(&huart2, rxbuf, 1);
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  while (1) {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(char *file, uint32_t line)
{ 
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
   tex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
