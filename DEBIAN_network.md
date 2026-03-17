# 连接子路由器的lan口无法上网
ip route show
default via 192.168.10.2 dev eth0 proto dhcp metric 100
你的鲁班猫现在的默认网关被错误地设置为了 192.168.10.2(子路由ip)：
你的主路由器 IP 是 192.168.10.1，那么所有的互联网请求（包括 DNS 解析和 Git 克隆）现在都发往了一个不存在的（或者不是路由器的）.2 设备，导致请求全部“石沉大海”。
sudo ip route del default via 192.168.10.2
sudo ip route add default via 192.168.10.1
强制刷新 DNS 缓存
echo "nameserver 114.114.114.114" | sudo tee /etc/resolv.conf

# vscode ssh连接

1)VS Code安装Remote Explorer
2)右下角打开远程窗口
3)ssh cat@192.168.10.109(lubancat ip)