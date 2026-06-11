# printf

在 syscalls.c:35 里，_write 会逐字节调用 __io_putchar；但工程里没有__io_putchar 的实际实现，所以 printf 没有真正发到串口。关键位置在 syscalls.c:80。

下面给你完整可用配置教程。
在 main.c 顶部补充头文件
把 string.h 加上（你已经有 stdio.h）。

# include "string.h"

在 main.c 的 USER CODE 区添加 __io_putchar
推荐放在 USER CODE BEGIN 4 区域，避免被 CubeMX 覆盖。

int __io_putchar(int ch)
{
HAL_UART_Transmit(&huart2, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
return ch;
}

可选：如果你希望输入重定向（如 scanf），再加 __io_getchar：

int __io_getchar(void){  uint8_t ch = 0;  HAL_UART_Receive(&huart2, &ch, 1, HAL_MAX_DELAY);  return ch;}

在 main 中确认初始化顺序
你现在顺序是对的：HAL_Init -> 时钟 -> GPIO -> USART2。
确保 printf 出现在 USART2 初始化之后，例如在 main.c:155 之后再调用。

直接测试 printf
在 main.c:158 附近加测试语句：

printf("printf OK, tick=%lu\r\n", HAL_GetTick());

串口工具参数
波特率 115200，8 数据位，1 停止位，无校验，无流控（与你配置一致，见 main.c:216）。

硬件连线检查（非常关键）
如果你是 NUCLEO 等带 ST-LINK VCP 的板，通常 USART2 PA2/PA3 已接到虚拟串口。
如果是最小系统板，PA2/PA3 需要外接 USB-TTL：
TX(PA2) -> USB-TTL RX
RX(PA3) -> USB-TTL TX
GND 共地。

如果要打印浮点 %f（可选）
默认很多嵌入式工程不带 float printf。你用 CMake 时，给链接选项加：

-u _printf_float

可在 CMakeLists.txt 的 add_link_options 那里加入。否则整数能打，浮点可能显示异常。

为什么这样就能好

调用链是：
printf -> _write -> __io_putchar -> HAL_UART_Transmit -> USART2 TX(PA2)

你现在缺的正是 __io_putchar 这一步，所以 printf 没有出口。补上后，syscalls 的弱符号机制会自动走到你的实现。

你当前代码里额外建议

你声明了 fputc 原型但未实现，见 main.c:60。如果改用 __io_putchar 方案，这个声明可以删掉，避免误导。
你已有 HAL_printf 函数，见 main.c:67。后续可以统一只用 printf，减少两套输出接口。
如果你愿意，我下一步可以按你工程现状给出“精确到插入位置”的 main.c 修改块（按 USER CODE 分区），你直接粘贴即可。
