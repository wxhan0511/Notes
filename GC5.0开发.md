## 1 LDO TPS7A4701RGWR
![alt text](pics/LDO/功能框图.png)
### LDO Input and Output Voltage Calculation Formula
![alt text](pics/LDO/LDO%20Input%20and%20Output%20Voltage%20Calculation%20Formula.png)
### Internal Principles of LDO
![alt text](pics/LDO/Internal%20Principles%20of%20LDO.jpg)

## 2 CD4051BPWR

![alt text](<CD405xB 具有逻辑电平转换功能的 CMOS 单路 8 通道.png>)

## 3 运算放大器

### 3.1 反相放大器 
该放大器在输入端接受正电压，然后使电压变为同样幅度的负电压。它还会以相同的方式使负输入电压变为正电压。
![alt text](pics/反相放大器典型应用.png)
### 3.2 同相放大器
![alt text](pics/同相放大器.png)
### 3.3 开环增益（开环放大倍数，A_ol）：
运放在不接外部反馈（即“开环”）时，输出对差分输入电压的放大倍数。数学上：
V_out = A_ol × (V+ − V−)。理想运放 A_ol 很大（十万到百万量级）；实际运放随频率下降。
### 3.4 闭环增益（闭环放大倍数，A_cl）：
在接入反馈网络后，实际电路对输入的放大倍数。对于负反馈系统，闭环增益由运放与反馈因子 β 共同决定，精确关系为：
A_cl = A_ol / (1 + A_ol·β)。
当 A_ol → ∞ 时，A_cl ≈ 1/β（即闭环由反馈网络决定，与运放本身无关）。
常见结果（直观公式）：
反相放大器：A_cl = −R_f / R_in（由电阻比决定，负号表示相位翻转）
同相放大器：A_cl = 1 + R_f / R_g（由电阻比决定）
电压跟随（缓冲）：A_cl = 1（β = 1）
### 3.5 什么是单位增益带宽（GBW）Unity Gain Bandwidth：
这是运放在闭环增益为 1（跟随器）时还能保持有效放大的最高频率
### 3.6 其他几种电路的链接
https://cloud.tencent.com/developer/article/2290991

## 4 LGS63042B5 (60V 降压型、升降压型 LED 恒流驱动器)
![alt text](pics/LGS63042B5/image.png)
LGS63042 支持数字输入（100HZ~100KHZ）的PWM 调光，高频 PWM 输入下无屏闪。调光比在PWM 频率为 100HZ 时高达 25000:1。
LED 的亮度是由PWM 信号的占空比决定的。例如 PWM 信号 25%占空比，LED 的平均电流为(0.2/RSence)的 25%。建议设置PWM 调光频率在 120Hz 以上，以避免人的眼睛可以看到 LED 的闪烁
![alt text](image.png)
肖特基二极管具有较低的正向电压降和较快的开关速度，
https://cloud.tencent.com/developer/article/2028590