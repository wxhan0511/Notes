# 连接子路由器的lan口无法上网
ip route show
default via 192.168.10.2 dev eth0 proto dhcp metric 100
你的鲁班猫现在的默认网关被错误地设置为了 192.168.10.2(子路由ip)：
你的主路由器 IP 是 192.168.10.1，那么所有的互联网请求（包括 DNS 解析和 Git 克隆）现在都发往了一个不存在的（或者不是路由器的）.2 设备，导致请求全部“石沉大海”。
sudo ip route del default via 192.168.10.2
sudo ip route add default via 192.168.10.1
强制刷新 DNS 缓存
echo "nameserver 114.114.114.114" | sudo tee /etc/resolv.conf

default via 192.168.10.1 dev eth1 proto dhcp metric 100
default via 172.30.88.1 dev wlan0 proto dhcp metric 600
172.30.88.0/21 dev wlan0 proto kernel scope link src 172.30.88.251 metric 600
192.168.10.0/24 dev eth1 proto kernel scope link src 192.168.10.107 metric 100
详细解释
default：默认路由（目标不匹配其他更具体网段时用它）
via 192.168.10.1：下一跳网关是 192.168.10.1
dev eth1：从有线网卡 eth1 发出
proto dhcp：这条路由由 DHCP 下发
metric 100：优先级，越小越优先,eth1 不可用时，系统可能切到 wlan0

到 172.30.88.0/21 网段（即 172.30.88.0 ~ 172.30.95.255）的流量
直接从 wlan0 发，不经网关（scope link）本地网段通信：不经网关,外网/其他网段：经默认网关
默认源地址用 172.30.88.251
# 登陆方式
## vscode ssh连接

1)VS Code安装Remote Explorer
2)右下角打开远程窗口
3)ssh cat@192.168.10.109(lubancat ip)

## 串口连接

# use_reloader=True 时，python debug的时候为什么要设false
    socketio.run(app, host=config.HTTP_HOST, port=config.HTTP_PORT, debug=config.DEBUG, use_reloader=False, allow_unsafe_werkzeug=True)

开启时：Flask 会启动 两个进程：一个主进程负责监控文件变化，另一个子进程才是真正的 Web 服务。
后果：IDE（如 VS Code）的调试器通常只能自动挂载到主进程上。当主进程启动子进程运行代码时，调试器往往无法“抓”住真正的执行代码。你打的断点会因为在不同进程中而失效。

当你运行程序时，Flask (Socket.IO) 的内部工作流程如下：

启动主进程（Parent Process）：

主进程启动，开始执行你的 main.py。
它会运行到 create_app()，并触发你代码中检测调试器的逻辑。
第一次打印：调试环境检测：未检测到调试器...
主进程的任务不是运行 Web 服务，而是盯着你的硬盘看文件有没有改动。
派生子进程（Child Process / Reloader Process）：

主进程立即通过命令行再次调用你自己，启动一个完全一样的子进程。
子进程从头开始重新跑一遍 main.py 的代码。
第二次打印：调试环境检测：未检测到调试器...
此时，子进程才会真正去初始化硬件（HAL）、监听端口（5000 和 9001）。
