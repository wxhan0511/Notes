# dwt

```c
static void DWT_Timer_Init(void)
{
  dwt_cycles_per_us = HAL_RCC_GetHCLKFreq() / 1000000U;
  printf("HCLK Frequency: %lu Hz\r\n", HAL_RCC_GetHCLKFreq());
  if (dwt_cycles_per_us == 0U)
  {
    dwt_cycles_per_us = 1U;
  }

  CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
  DWT->CYCCNT = 0U;
  DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}
// dwt_cycles_per_us = 36,000,000 / 1,000,000
//                   = 36
static uint32_t DWT_GetUs(void)
{
  return DWT->CYCCNT / dwt_cycles_per_us;
}
// DWT 计数器每增加 36 → 时间 +1us
```
