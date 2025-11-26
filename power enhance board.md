# 项目说明

一、ADS1256采样值raw_data使用一个循环队列（环形缓冲区）来存储，存放在RAM中

    1、在 LD 文件中为环形队列分配空间，添加一个新的段用于环形队列
    2、将raw_data 数据放入环形队列，满了则覆盖最早的数据

二、测试记录
MCP4728
实测：4路输出均为1500mv
万用表测量结果:
-7.7V:ELVSS
-7.26V:ELVDD
-10.12V:VBAT
程序采样结果,mA档:
channel0:4091220.544000  AD_V_VBAT 
channel1:2838365.368000  AD_V_ELVDD
channel2:3038473.560000  AD_V_ELVSS
channel3:4180.344000     AD_I_VBAT
channel4:4154.716000     AD_I_ELVDD
channel5:2499936.304000  2.5Vref
channel6:1185.444000     AD_I_ELVSS
uA档:
channel0:4091018.500000   AD_V_VBAT
channel1:2838263.452000   AD_V_ELVDD
channel2:3038379.392000   AD_V_ELVSS
channel3:248784.108000      AD_I_VBAT
channel4:237404.680000      AD_I_ELVDD
channel5:2499898.160000      2.5Vref
channel6:74933.888000       AD_I_ELVSS
校准

Ilim_DA+    报警电流=设定电压*5/6（单位A）
ADJ_VBAT    
ADJ_ELVDD+
ADJ_ELVSS

-  校准电流电压采样 精度1% 暂停
<details>
电压
    公式：mA档电流：I=500Vi uA档电流：I=100Vi
    VBAT Vi=1200mv 实际Vo=11.07V 理论Vo=12.0556V   //最大限制大概11V    有效设定范围+1.4V~Vin    vi范围
    VBAT Vi=1500mv 实际Vo=10.21V 理论Vo=10.3195V    理论-实际=0.1095
    VBAT Vi=1800mv 实际Vo=8.47V  理论Vo=8.5834V     理论-实际=0.1134
    VBAT Vi=2100mv 实际Vo=6.73V  理论Vo=6.8473V     理论-实际=0.1173
    VBAT Vi=2400mv 实际Vo=4.99V  理论Vo=5.1112V     理论-实际=0.1212    四次平均为0.11535
    公式VBAT+=19-5.787Vi        加入偏差计算:vi = (19 - (Vo + bias))/5.787
    ELVDD Vi=2300mv 实际Vo=6.60v 理论Vo=6.5352               //最大限制大概7V    有效设定范围+1.4V~V+_ADJ    2.22<vi范围<3.08v
    ELVDD Vi=2400mv 实际Vo=5.95v 理论Vo=5.8776      理论-实际=-0.0734
    ELVDD Vi=2600mv 实际Vo=4.64v 理论Vo=4.5624      理论-实际=-0.0776
    ELVDD Vi=2700mv 实际Vo=3.986v 理论Vo=3.9048     理论-实际=-0.0812
    ELVDD Vi=2800mv 实际Vo=3.34v 理论Vo=3.2472      理论-实际=-0.0928    四次平均为0.08125
    公式ELVDD+=21.66-6.576Vi    加入偏差计算:vi = (21.66 - (Vo + bias))/6.576
    ELVSS                                           //最小限制大概-7V   有效设定范围-1.4V~V-_ADJ    vi范围<3.08v
    ELVSS Vi=2500mv 实际Vo=-2.071V  理论Vo= -1.85v  理论-实际=0.221
    ELVSS Vi=2300mv 实际Vo=-3.646V  理论Vo= -3.436v 理论-实际=0.21
    ELVSS Vi=2000mv 实际Vo=-6.020V  理论Vo= -5.815v 理论-实际=0.205
    ELVSS Vi=1800mv 实际Vo=-7.58V  理论Vo= -7.401V  理论-实际=0.179      四次平均为 0.20375
    ELVSS Vi=1500mv 实际Vo= -8.25v 理论Vo= -9.78v   理论-实际=
    公式Vo=21.675-7.93Vi        加入偏差计算:vi = (21.675 - (Vo + bias))/7.93
电流
    VBAT Vi=1800mv   实际8.01mA 采样8.511mA         采样-实际=0.501                      无负载2.180mA
    VBAT Vi=1500mv   实际9.66mA 采样10.262mA        采样-实际=0.602
    VBAT Vi=2100mv   实际6.37mA 采样6.849mA         采样-实际=0.479      三次平均 = 0.527
    VBAT Vi=2200mv   实际6.37mA 采样6.849mA
    ELVDD Vi=2200mv       6.88  8.612              采样-实际= 1.732                             无负载2.160mA
    ELVDD Vi=2400mv       5.64 7.147               采样-实际= 1.507
    ELVDD vi=2700mv       3.78 4.907               采样-实际= 1.127     三次平均 = 1.455
    ELVDD                 3.78 4.887
    ELVSS Vi=2500mv   实际-1.94mA 采样-2.685mA      采样-实际= -0.745
    ELVSS Vi=2300mv   实际-3.42mA 采样-4.198mA      采样-实际= -0.778   二次平均=0.7615 无负载-0.548mA
-- 测试电压使能信号  ELVSSEN待硬件更正

--上电时序控制逻辑
<details>
    1.Set_EXT_POWER();




发布电源增强板校准

VBAT电流 

ELVDD+=21.66-6.576Vi
ELVSS-=-(18.19-6.576Vi)
VBAT+=18.88-5.787Vi

VBAT 
实际25.9mA,采样45.296




































三、问题
168MSCLK跑飞，规避措施：降频至76M不跑飞 问题原因:i2c线程中有大量串口打印,去掉之后就好了
四、FreeRTOS常见问题
1、任务资源调用冲突
两个任务在运行中可能调用同一个串口，在一个任务使用串口的过程中，被另一个高优先级的任务中断，然后低优先级的任务就死掉了
在串口的使用中加入互斥变量，保证串口只能同时被单独一个任务调用
（2）程序的堆栈开的比较小，可能程序在执行一段时间之后，堆栈的使用越来越多，之后就会导致堆栈溢出，该任务死掉
解决方法是：在任务调试的阶段使用   uxTaskGetStackHighWaterMark() 来查询任务堆栈的使用情况，如果不够，及时增大堆栈
（3）时间片调度没有打开
FreeRTOS.h   文件中宏定义 configUSE_TIME_SLICING 没有定义为1
(4)中断函数中定义了，SVC_Handler，PendSV_Handler，SysTick_Handler 三个中断，导致FreeRTOS中的 port.c 文件中的任务调度函数无法执行，任务无法切换。
解决方案：
删除自定义的 SVC_Handler，PendSV_Handler，SysTick_Handler，三个中断函数
（5）、问题
在 FreeRTOS 启动后（即 osKernelStart() 之后），不能再用 HAL_Delay，因为此时 SysTick 已被 FreeRTOS接管，HAL_Delay 可能无法正常递增 uwTick，导致死循环
SysTick 定时器在 FreeRTOS 中的主要用途是作为系统节拍定时器（系统时钟），用于实现任务调度和时间管理

四、

1. I2C 通信线
SCL/SDA：主从板 I2C1 的 SCL、SDA 线直接连接（如 PB6/SCL, PB7/SDA），并加上拉电阻。
2. 通知信号线（用于外部中断）
//PB0、PB1 配置为 GPIO_EXTI（上升沿/下降沿触发）
//PD2、PD3 配置为 GPIO_Output
//从机 PD3 ——> 主机 PB0、主机 PD2 ——> 从机 PB1  
3. 总结连接表
信号功能 主机IO 从机IO 连接方式·
I2C SCL PB6 PB6 直接连接
I2C SDA PB7 PB7 直接连接
主机通知从机 PD2（输出） PB1（EXTI输入） PD2 → PB1
从机通知主机 PD3（EXTI输入） PB0（EXTI输入） PD3 → PB0
4. 说明
主机要发数据时，拉高 PD2，触发从机 PB1 的外部中断（EXTI），从机开始接收。
从机准备好数据后，拉高 PD3，触发主机 PB0 的外部中断（EXTI），主机开始读取。
两端都可以用 HAL_GPIO_EXTI_Callback 检测对方通知信号。
调用后，函数立即返回，I2C数据发送过程由硬件和中断自动完成。发送完成后会自动进入回调函数（HAL_I2C_MasterTxCpltCallback），你可以在回调里设置标志位或通知任务。
优点：
非阻塞，CPU可以继续做其他任务，提高系统并发和实时性，适合RTOS环境。
注意：

IO线建议加上拉/下拉电阻，防止误触发。
连接时注意地线共地

五、I2C

5.1、I2C配置

1. I2C主机配置  
    - 使用 HAL_I2C_Init(&hi2c1) 初始化 I2C1。  
    - 设置时钟速度为 100kHz，地址模式为 7 位。  
    - 主机地址设置为 0x30（7 位地址）。

2. I2C从机配置  
    - 使用 HAL_I2C_Init(&hi2c1) 初始化 I2C1。  
    - 设置时钟速度为 100kHz，地址模式为 7 位。  
    - 从机地址设置为 0x30（7 位地址）。

3. I2C中断配置  
    - 使用 HAL_NVIC_SetPriority 和 HAL_NVIC_EnableIRQ 配置 I2C1 中断。  
    - 在中断回调函数中处理 I2C 事件和错误。

4. I2C使能  
    - 使用 HAL_I2C_EnableListen_IT(&hi2c1) 使能监听模式。  
    - 监听模式使能后，从机会自动响应主机的寻址请求。

5.2、I2C从机监听以及主从接收发送数据

1. 从机监听使能  
    - 从机在初始化时调用 HAL_I2C_EnableListen_IT(&hi2c1) 使能监听模式。  
    - 这会使从机进入监听状态，等待主机的寻址请求。

2. 主机寻址  
    - 主机通过 I2C 寻址从机时，发送 START 信号和从机地址。  
    - 从机在监听状态下会自动响应。

3. 从机响应  
    - HAL_I2C_ListenCpltCallback 回调函数会在地址匹配上以后被调用。
    - HAL_I2C_AddrCallback 回调函数会在地址匹配上以后被调用。
4. 从机接收数据
    - 使用 HAL_I2C_Slave_Receive_IT 函数接收数据。

5. 从机发送数据
     - 从机可以使用 HAL_I2C_Slave_Transmit_IT(&hi2c1, tx_buf, size) 函数发送数据。

5.3、主机发送数据到从机

1. 主机发送数据  
     - 主机可以通过 HAL_I2C_Master_Transmit 函数发送数据到从机。

问题
//MASTER复位可以正常发，slave正常接收
1、SLAVE复位，没人接，SCL线被主机拉低


2、主机调用 HAL_I2C_EnableListen_IT 后，会导致主机无法正常发送 HAL_I2C_Master_Transmit，原因如下:

HAL_I2C_EnableListen_IT 的作用是让I2C外设进入从机监听模式，等待主机寻址并响应。
当你调用这个函数后，I2C外设会配置为从机模式，并使能地址匹配等中断。
STM32的I2C外设同一时刻只能作为主机或从机，不能既监听又主动发起通信。
如果你在主机端调用了 HAL_I2C_EnableListen_IT，I2C外设会被配置为从机，主机功能被禁止，此时再调用 HAL_I2C_Master_Transmit，I2C不会发起主机通信

3、主机调用HAL_I2C_Master_Transmit_IT(&hi2c1, SLAVE_ADDR, tx_buf, DATA_SIZE)后，从机不ACK，此时主机将SCL拉低，保持常低，会进入I2C1_ER_IRQHandler->HAL_I2C_ErrorCallback
4、

i2c寄存器详解
1. I2C_CR1（控制寄存器1）
控制I2C外设的使能、ACK应答、启动/停止信号、软件复位等。
主要位：
PE：I2C外设使能
START：产生起始信号
STOP：产生停止信号
ACK：应答使能
当主机发送地址，从机地址匹配时，且ACK位已使能，从机会自动在第9个时钟周期拉低SDA，发出ACK应答
每接收一个字节数据，只要ACK位为1，从机会在第9个时钟周期自动发ACK。
如果ACK位为0，则发NACK（不应答
SWRST：软件复位
2. I2C_CR2（控制寄存器2）
配置I2C外设的时钟、DMA、错误/事件/缓冲中断等。
主要位：
FREQ[5:0]：APB1时钟频率（MHz）
ITERREN：错误中断使能
ITEVTEN：事件中断使能
ITBUFEN：缓冲中断使能
3. I2C_OAR1（本机地址寄存器1）
设置I2C从机的主地址（7位或10位）。
主要位：
ADD[9:0]：本机地址
ADDMODE：地址模式（0=7位，1=10位）
4. I2C_OAR2（本机地址寄存器2）
设置第二个从机地址（一般用于双地址响应）。
主要位：
ENDUAL：双地址使能
ADD2[7:1]：第二地址
5. I2C_DR（数据寄存器）
发送或接收I2C数据的寄存器。
读：接收数据，写：发送数据。
6. I2C_SR1（状态寄存器1）
反映I2C通信过程中的各种事件和错误状态。
主要位：
SB：起始位已发送
ADDR：地址已发送/匹配
BTF：字节传输完成
RXNE：接收缓冲区非空
TXE：发送缓冲区空
AF：应答失败（NACK）
STOPF：检测到停止信号
OVR：溢出
ARLO：仲裁丢失
BERR：总线错误
7. I2C_SR2（状态寄存器2）
反映I2C外设的总线状态和主/从状态。
主要位：
MSL：主/从模式
BUSY：总线忙
TRA：发送/接收模式
DUALF：第二地址匹配
8. I2C_CCR（时钟控制寄存器）
配置I2C SCL时钟频率（标准/快速模式）。
主要位：
CCR[11:0]：时钟控制
FS：快速模式选择
DUTY：快速模式占空比
9. I2C_TRISE（最大上升时间寄存器）
设置SCL信号的最大上升时间（单位为APB1时钟周期）。
10. I2C_FLTR（数字滤波器寄存器）
配置I2C数字滤波器和模拟滤波器功能。