这里是获取各系列 STM32 Demo 库的最快路径与目录结构要点：

一、官方 STM32Cube MCU 包（含 HAL/LL、BSP、Examples、Applications、Demos）

入口页（按系列下载）:
STM32Cube 全系列列表: https://www.st.com/en/embedded-software/stm32cube-mcu-packages.html
直接访问常用系列：
F0: https://www.st.com/en/embedded-software/stm32cubef0.html
F1: https://www.st.com/en/embedded-software/stm32cubef1.html
F3: https://www.st.com/en/embedded-software/stm32cubef3.html
F4: https://www.st.com/en/embedded-software/stm32cubef4.html
F7: https://www.st.com/en/embedded-software/stm32cubef7.html
G0: https://www.st.com/en/embedded-software/stm32cubeg0.html
G4: https://www.st.com/en/embedded-software/stm32cubeg4.html
H7: https://www.st.com/en/embedded-software/stm32cubeh7.html
L0/L1/L4/L5: 对应 STM32CubeL0/L1/L4/L5 页面
无线（WB/WBA/WL）：STM32CubeWB / STM32CubeWBA / STM32CubeWL
安装后在 Windows 默认路径：
C:\Users\你的用户名\STM32Cube\Repository\STM32Cube_FW_F4_Vx.y.z\
目录结构要点：
Drivers/：HAL/LL/BSP
Middlewares/：USB、FreeRTOS、LWIP 等
Projects/开发板/Examples/：HAL 示例
Projects/开发板/Examples_LL/：LL 示例
Projects/开发板/Applications/：USB/CMSIS-RTOS/文件系统等应用示例
Projects/开发板/Demonstrations/：演示工程
二、GitHub 官方镜像（便于按系列克隆）

组织地址：https://github.com/STMicroelectronics
常用仓库：
https://github.com/STMicroelectronics/STM32CubeF0
https://github.com/STMicroelectronics/STM32CubeF1
https://github.com/STMicroelectronics/STM32CubeF3
https://github.com/STMicroelectronics/STM32CubeF4
https://github.com/STMicroelectronics/STM32CubeF7
https://github.com/STMicroelectronics/STM32CubeG0
https://github.com/STMicroelectronics/STM32CubeG4
https://github.com/STMicroelectronics/STM32CubeH7
以及 L0/L1/L4/L5、WB/WBA/WL 等对应仓库
三、用 STM32CubeMX 安装示例（推荐）

打开 STM32CubeMX → Help → Manage embedded software packages
勾选对应系列（如 STM32CubeF4）安装
示例路径同上 Repository 目录中的 Projects/.../Examples 与 Applications
可直接在 CubeMX 里“New Project from Example”，选择目标 MCU/开发板的示例工程生成
四、如何快速定位你要的 Demo

HAL 基础外设示例：Projects/板卡/Examples/<Periph名>/
LL 版本示例：Projects/板卡/Examples_LL/<Periph名>/
USB 设备/主机示例：Projects/板卡/Applications/USB_Device 或 USB_Host（如 HID、CDC、MSC、Custom HID）
RTOS 示例：Projects/板卡/Applications/FreeRTOS 或 CMSIS-RTOS
网络/LWIP/文件系统：在 Applications 下对应子目录