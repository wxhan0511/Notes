
## 编辑
### 粘贴
Vim 开启“粘贴模式”
如果你习惯用 vim，必须先进入粘贴模式，否则它会自动帮你“无限缩进”。

打开文件：vi quick_start/spi/spi_selftest.c
按下 Esc 键，输入 :set paste 然后按回车。
按下 i 进入插入模式（此时下方会显示 -- INSERT (paste) --）。
粘贴内容。
粘贴完后，按 Esc，输入 :set nopaste 恢复正常模式，最后输入 :wq 保存。

:set paste 在 Vim 中的作用是关闭所有“聪明”的自动排版功能
1. 拆解这几个符号（底层含义）
\n (Line Feed, LF)：换行。意思是把纸往上挪一行，但光标位置不动。
\r (Carriage Return, CR)：回车。意思是把打印针头推回这行的最左边。
2. 为什么 Linux 不行？
Linux 的逻辑：认为一个 \n 就够了，它默认包含了“换行+回道首”的操作。
Windows 的逻辑：坚持模拟古老的打字机，必须先“回车（\r）”再“换行（\n）”。
## 创建
mkdir -p quick_start/spi
parents 递归创建
## 编译和运行
#编译
gcc spi_selftest.c -o spi_selftest
#运行
sudo ./spi_selftest /dev/spidev0.0
## 常用命令
sudo reboot 进行重启应用
sudo 的全称是：Super User Do
rm  文件名
rm -r 文件夹名
rm -f test.txt 强制删除且不提示，加 -f 参数
touch 文件名
echo "内容" > 文件名
ls -a a:all
## 安装
sudo apt install
## 代码常用函数
sleep(秒级延时)
头文件：#include <unistd.h>
用法：sleep(1); // 延时1秒

## io
出现 -bash: echo: 写错误: 设备或资源忙，说明 GPIO7 已经被导出（export），或者有其他进程正在占用该 GPIO。
解决方法：
1. 先取消导出（unexport）：
echo 7 > /sys/class/gpio/unexport
2. 再重新导出：
echo 7 > /sys/class/gpio/export
这样就可以正常操作了。
#以下所有操作均需要打开管理者权限使用
#使能引脚GPIO1_C4
echo 52 > /sys/class/gpio/export

#设置引脚为输入模式
echo in > /sys/class/gpio/gpio52/direction
#读取引脚的值
cat /sys/class/gpio/gpio52/value

#设置引脚为输出模式
echo out > /sys/class/gpio/gpio52/direction
#设置引脚为低电平
echo 0 > /sys/class/gpio/gpio52/value
#设置引脚为高电平
echo 1 > /sys/class/gpio/gpio52/value

#复位引脚
echo 52 > /sys/class/gpio/unexport
## 包
(Advanced Packaging Tool)
sudo apt update
sudo apt -y install
## 链接
(link)
(-s：是 --symbolic)
#设置软链接，python默认使用python3
sudo ln -s /usr/bin/python3 /usr/bin/python

#设置软链接，pip默认使用pip3
sudo ln -s /usr/bin/pip3 /usr/bin/pip

不加s是硬链接
Linux 里的文件，本质是 “数据块 + 文件名（索引）”，每个文件名都是对数据块的一次引用：
创建硬链接时，系统会给文件的「引用计数」+1（比如源文件是 1，硬链接后变成 2）；
删除文件（rm）时，系统只做两件事：① 删除文件名 ② 引用计数 - 1；
只有当「引用计数 = 0」时，系统才会真正删除文件本体（数据块

## 看端口占用
sudo ss -ltnp | grep :5000
ss
Linux 下查看 socket（网络连接/监听端口）的工具，替代 netstat。
-l (--listening)
只看“监听中”的端口（服务端口），不看已建立连接。

-t
只看 TCP。
（如果你要看 UDP，用 -u）

-n
地址和端口用数字显示，不做 DNS/服务名解析，速度更快更直观。
例如直接显示 0.0.0.0:5000，不会变成 *:http-alt 之类。

-p
显示占用该端口的进程信息（pid 和程序名）。

|
管道，把前面输出传给后面命令过滤。

grep :5000
只保留包含 :5000 的行，即只看 5000 端口

sudo kill -9 849 2021
-9 参数表示强制杀死进程。
sudo fuser -k 5000/tcp
fuser (File User) 用于显示哪些进程正在使用指定的文件、目录或套接字