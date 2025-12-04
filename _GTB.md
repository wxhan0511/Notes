# GTB Develop GUIDE

## GTB 报点 config

### GTB version
![alt text](pics/GTB/3.png)
### 初始化代码
Notes\GTB\7272+BOE_longV验证代码20230413_70M_4.0.zip
### BIN
Notes\GTB\GC7272.bin
### 屏
![alt text](pics/GTB/lQDPKeC-T8_wJvPNB4DNBaCwi0O6aTjCLOcJC97To7wYAA_1440_1920.jpg)
### 底板固件
Notes\GTB\AE_Tool_Firmware_0538090A.bin
### step
1、![alt text](pics/GTB/1.png)
2、按waitkey 屏幕亮
3、![alt text](pics/GTB/2.png)




## 通过GTB板进行SPI烧录
### sleep in ， sleepout ，dispon
![alt text](pics/GTB/GTB_SPI_FLASHDOWNLOAD烧录/lQLPJwFvSLAG8FfM880B-bCN05RNTQXnRwj18wetqZQA_505_243.png)
![alt text](pics/GTB/GTB_SPI_FLASHDOWNLOAD烧录/0bd5e47d0e6e4797b51b60fca091014e.png)
![alt text](pics/GTB/GTB_SPI_FLASHDOWNLOAD烧录/a092e7b6360f4b79b075b95e985da5f5.png)
### 环境
![alt text](pics/GTB/GTB_SPI_FLASHDOWNLOAD烧录/image-14.png)
![alt text](pics/GTB/GTB_SPI_FLASHDOWNLOAD烧录/DINGTALK_IM_2516544819.JPG.JPG)
![alt text](pics/GTB/GTB_SPI_FLASHDOWNLOAD烧录/DINGTALK_IM_400944706.JPG.JPG)
![alt text](pics/GTB/GTB_SPI_FLASHDOWNLOAD烧录/DINGTALK_IM_729496886.JPG.JPG)


## STM32作为下位机

STM32 specifies UID and PID
![alt text](pics/GTB/image-28.png)

Transplant from User\thread\src\server_gtb.c

GC4.0底板
HOST to DEVICE
USBD_HID0_SetReport

DEVICE_TO_HOST
USBD_HID_GetReportTrigger