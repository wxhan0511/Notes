# ESP32-IDF
ESP-IDF安装管理器（EIM）是一个统一工具，简化了跨多个平台的ESP-IDF及集成开发环境（IDE）的设置流程。
VSCODE下载ESP-IDF扩展
离线下载安装包5.5.3




## 配置

### 设置乐鑫设备目标

ESP32-WROOM-32D : 乐鑫通用型 Wi-Fi + Bluetooth®+ Bluetooth LE MCU 模组



Espressif 官方开发板（例如 WROVER Kit / 开发板带 JTAG），选对应的条目：开发板为 WROVER Kit 且供电 3.3V → 选 “ESP‑WROVER‑KIT 3.3V”。
单独的 ESP32‑WROOM‑32E（裸模块）并且用外接 ESP‑PROG 调试器连接 → 选 “ESP32 chip (via ESP‑PROG)”（或 ESP‑PROG‑2，取决于你用哪代硬件）。

你用裸模块且只通过串口刷写时，不需要在“OpenOCD 配置文件路径”里选择板/接口；在扩展里只需选择串口（选择要使用的端口 / 选择要使用的监视端口），用 idf.py -p <port> flash monitor 完成刷写与监视。

具体步骤（最少必做）

硬件连线：


EN/RESET 用于复位（短按实现）
在 VS Code ESP‑IDF 扩展中：

在命令面板运行 ESP‑IDF: Select port（或 选择要使用的端口），选择你的 COM 号（例如 COM3）。
选择要使用的监视端口 可与刷写端口相同。
不要填写 OpenOCD 配置（OpenOCD 仅用于 JTAG 调试）。若扩展强制要求，从下拉选“Custom board”，但不必配置 OpenOCD。
手动进入下载模式（若适配器不支持 DTR/RTS 自动切换）：

把 IO0 拉低（短接到 GND）。
短按 EN（或断电再上电）以复位。
松开 IO0（或保持直到 esptool 开始）。模块即进入 bootloader 等待刷写。
常用命令（在项目根目录）：

构建：
idf.py build
刷写并自动打开监视（推荐）：
idf.py -p COM3 flash monitor
（把 COM3 换成你的端口；如需指定波特：-b 115200）
说明 OpenOCD 下拉列表如何选：

仅串口刷写（不做 JTAG 调试）：无需选 OpenOCD 条目或填写 OpenOCD 路径。选择串口即可。
如果你以后想用 JTAG 调试（需要断点/单步），那才在 OpenOCD 列表选 ESP32 chip (via ESP‑PROG)（或对应你的调试器），并接好 JTAG 线。
快速排错：

串口打不开：关闭占用串口的其它程序（如其它终端）。
刷写失败：确认 TX/RX 没接反、GND 共地、VCC 为 3.3V、IO0 在正确时间拉低。
看不到日志：确认 monitor 使用正确端口、波特率与项目一致（通常 115200）。


### 环境

### python

打开ESP-IDF终端
idf.py set-target ESP32
idf.py dfu
###
