
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
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "stm32l4xx_hal.h"
#include "dac.h"
#include "dfsdm.h"
#include "dma.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* USER CODE BEGIN Includes */
#include "stdbool.h"
#include "arm_math.h"
#include "math.h"
#include "stdio.h"
#include "dsp.h"
/* USER CODE END Includes */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

// N/2
const int NN_HALF = NN / 2;

// flag: "new PCM data has just been copied to buf"
volatile bool new_pcm_data_a = false;
volatile bool new_pcm_data_b = false;

// output trigger
volatile bool printing = false;

// UART output mode
volatile mode output_mode = FILTERED_MEL;
mode filter_type = FILTERED_MEL;

// UART input
uint8_t rxbuf[1];

/* Private variables ---------------------------------------------------------*/

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);

/* USER CODE BEGIN PFP */
/* Private function prototypes -----------------------------------------------*/

/* USER CODE END PFP */

/* USER CODE BEGIN 0 */

bool uart_tx(float32_t *in, mode mode, bool dma_start) {

  bool printing;
  static int cnt = 0;
  static int length = 0;
  static int idx = 0;

  static char uart_buf[NN * 8] = { 0.0f };

  if (cnt == 0) {
    idx = 0;

    switch (mode) {

    case RAW_WAVE:
      length = NN;
      cnt = 1;
      break;

    case PSD:
      length = NN / 2;
      cnt = 1;
      break;

    case FILTERED_MEL:
      length = NUM_FILTERS;
      cnt = 200;
      break;

    case MFCC:
      length = NUM_FILTERS;
      cnt = 200;
      break;

    case MFCC_STREAMING:
      length = NUM_FILTERS;
      cnt = 0x7fffffff;
      break;

    case FILTERED_LINEAR:
      length = NUM_FILTERS_L;
      cnt = 200;
      break;

    default:
      length = 0;
      break;

    }
  }

  if (mode == FILTERBANK) {   // just dump filter bank itself
    for (int m = 1; m < NUM_FILTERS + 1; m++) {
      for (int i = 0; i < NN / 8; i++) {
        printf("%ld\n", (uint32_t) (filterbank[m][i] * 100.0));
      }
      if (m != NUM_FILTERS) printf("d\n");
    }
    printf("e\n");
    printing = false;

  } else {   // dump time-series signal

    for (int n = 0; n < length; n++) {
      idx += sprintf(&uart_buf[idx], "%ld\n", (int32_t) in[n]);
    }

    if (--cnt == 0) {
      idx += sprintf(&uart_buf[idx], "e\n");  // transmission end
      HAL_UART_Transmit_DMA(&huart2, (uint8_t *) uart_buf, idx);
      printing = false;
    } else if (dma_start) {
      idx += sprintf(&uart_buf[idx], "d\n");  // delimiter
      HAL_UART_Transmit_DMA(&huart2, (uint8_t *) uart_buf, idx);
      idx = 0;
      printing = true;
    } else {
      idx += sprintf(&uart_buf[idx], "d\n");  // delimiter
      printing = true;
    }
  }

  return printing;
}

/*
 * DSP pipeline
 */
void dsp(float32_t *s1, mode mode) {
//static bool p = true;
  static bool p = false;
  uint32_t start = 0;
  uint32_t end = 0;
  if (p)
    start = HAL_GetTick();
  switch (mode) {

  case RAW_WAVE:
    break;

  case MFCC:
  case FILTERED_MEL:
#ifdef PRE_EMPHASIS
    apply_pre_emphasis(s1);
#endif
  case FILTERED_LINEAR:
  case PSD:
    apply_hann(s1);
    apply_fft(s1);
    apply_psd_logscale(s1);
    switch (mode) {
    case PSD:
      break;
    case FILTERED_MEL:
    case FILTERED_LINEAR:
      if (filter_type != mode) {
        generate_filters(mode);
        filter_type = mode;
      }
      apply_filterbank(s1, mode);
      break;
    case MFCC:
      apply_filterbank(s1, mode);
      apply_dct2(s1);
      break;
    default:
      break;
    }
  default:
    break;
  }
  if (p) {
    end = HAL_GetTick();
    printf("%lu %lu\n", start, end);
    p = false;
  }
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  *
  * @retval None
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  // Audio sample rate and period
  float32_t sampling_frequency;

  // DMA peripheral-to-memory double buffer
  int32_t input_buf[NN * 2] = { 0 };

  // DMA memory-to-peripheral double buffer
  volatile uint16_t dac1_out1_buf[NN * 2] = { 0 };
  volatile uint16_t dac1_out2_buf[NN * 2] = { 0 };

  // PCM data store for further processing (FFT etc)
  float32_t signal[NN] = { 0.0f };
  float32_t signal_buf[NN + NN / 2] = { 0.0f };

  /* USER CODE END 1 */

  /* MCU Configuration----------------------------------------------------------*/

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
  MX_USART2_UART_Init();
  MX_DFSDM1_Init();
  MX_DAC1_Init();
  MX_TIM6_Init();
  /* USER CODE BEGIN 2 */

  sampling_frequency = SystemCoreClock
      / hdfsdm1_channel2.Init.OutputClock.Divider
      / hdfsdm1_filter0.Init.FilterParam.Oversampling
      / hdfsdm1_filter0.Init.FilterParam.IntOversampling;

  // DSP initialization
  init_dsp(sampling_frequency);

  // Start timer 6 and DAC for DMA
  HAL_TIM_Base_Start(&htim6);
  HAL_DAC_Start(&hdac1, DAC_CHANNEL_1);
  HAL_DAC_Start_DMA(&hdac1, DAC_CHANNEL_1, (uint32_t*) dac1_out1_buf, NN * 2,
  DAC_ALIGN_12B_R);
  HAL_DAC_Start(&hdac1, DAC_CHANNEL_2);
  HAL_DAC_Start_DMA(&hdac1, DAC_CHANNEL_2, (uint32_t*) dac1_out2_buf, NN * 2,
  DAC_ALIGN_12B_R);

  HAL_Delay(1);

  // Enable DMA from DFSDM to buf (peripheral to memory)
  if (HAL_DFSDM_FilterRegularStart_DMA(&hdfsdm1_filter0, input_buf, NN * 2)
      != HAL_OK) {
    Error_Handler();
  }

  // Enable UART receive interrupt
  HAL_UART_Receive_IT(&huart2, rxbuf, 1);

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1) {
    // Wait for next PCM samples from M1
    if (new_pcm_data_a) {

      for (uint32_t n = 0; n < NN; n++) {
        dac1_out1_buf[n] = (uint16_t) ((input_buf[n] >> 13) + 2048);
        dac1_out2_buf[n] = dac1_out1_buf[n];
      }

      arm_copy_f32(signal_buf + NN, signal_buf, NN_HALF);
      for (uint32_t n = 0; n < NN; n++) {
        signal_buf[n + NN_HALF] = (float32_t) (input_buf[n] >> 9);
      }

      arm_copy_f32(signal_buf, signal, NN);
      dsp(signal, output_mode);
      if (printing) {
        printing = uart_tx(signal, output_mode, false);
      }

      arm_copy_f32(signal_buf + NN_HALF, signal, NN);
      dsp(signal, output_mode);
      if (printing) {
        printing = uart_tx(signal, output_mode, true);
      }

      new_pcm_data_a = false;

    }

    if (new_pcm_data_b) {

      for (uint32_t n = NN; n < NN * 2; n++) {
        dac1_out1_buf[n] = (uint16_t) ((input_buf[n] >> 13) + 2048);
        dac1_out2_buf[n] = dac1_out1_buf[n];
      }

      arm_copy_f32(signal_buf + NN, signal_buf, NN_HALF);
      for (uint32_t n = 0; n < NN; n++) {
        signal_buf[n + NN_HALF] = (float32_t) (input_buf[n + NN] >> 9);
      }

      arm_copy_f32(signal_buf, signal, NN);
      dsp(signal, output_mode);
      if (printing) {
        printing = uart_tx(signal, output_mode, false);
      }

      arm_copy_f32(signal_buf + NN_HALF, signal, NN);
      dsp(signal, output_mode);
      if (printing) {
        printing = uart_tx(signal, output_mode, true);
      }

      new_pcm_data_b = false;
    }

  /* USER CODE END WHILE */

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

  RCC_OscInitTypeDef RCC_OscInitStruct;
  RCC_ClkInitTypeDef RCC_ClkInitStruct;
  RCC_PeriphCLKInitTypeDef PeriphClkInit;

    /**Initializes the CPU, AHB and APB busses clocks 
    */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = 16;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 1;
  RCC_OscInitStruct.PLL.PLLN = 10;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV7;
  RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV2;
  RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
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
    _Error_Handler(__FILE__, __LINE__);
  }

  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USART2|RCC_PERIPHCLK_DFSDM1;
  PeriphClkInit.Usart2ClockSelection = RCC_USART2CLKSOURCE_PCLK1;
  PeriphClkInit.Dfsdm1ClockSelection = RCC_DFSDM1CLKSOURCE_PCLK;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

    /**Configure the main internal regulator output voltage 
    */
  if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

    /**Configure the Systick interrupt time 
    */
  HAL_SYSTICK_Config(HAL_RCC_GetHCLKFreq()/1000);

    /**Configure the Systick 
    */
  HAL_SYSTICK_CLKSourceConfig(SYSTICK_CLKSOURCE_HCLK);

  /* SysTick_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(SysTick_IRQn, 0, 0);
}

/* USER CODE BEGIN 4 */
/**
 * @brief  Half regular conversion complete callback.
 * @param  hdfsdm_filter DFSDM filter handle.
 * @retval None
 */
void HAL_DFSDM_FilterRegConvHalfCpltCallback(
    DFSDM_Filter_HandleTypeDef *hdfsdm_filter) {
  if (!new_pcm_data_a && (hdfsdm_filter == &hdfsdm1_filter0)) {
    new_pcm_data_a = true;
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
  if (!new_pcm_data_b && (hdfsdm_filter == &hdfsdm1_filter0)) {
    new_pcm_data_b = true;
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

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
  if (GPIO_Pin == GPIO_PIN_13) {  // User button (blue tactile switch)
    printing = true;
  }
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
  output_mode = (mode) (rxbuf[0] - 0x30);
  printing = true;
  HAL_UART_Receive_IT(&huart2, rxbuf, 1);
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @param  file: The file name as string.
  * @param  line: The line in file as a number.
  * @retval None
  */
void _Error_Handler(char *file, int line)
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
void assert_failed(uint8_t* file, uint32_t line)
{ 
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
   tex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/**
  * @}
  */

/**
  * @}
  */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
