
## 虚拟环境
python3 --version
pip3 --version
python -m venv venv //虚拟环境创建
.\venv\Scripts\activate.bat  //激活
## 库路径
普通用户：在用户主目录下（~/.local/lib/），仅当前用户可访问；
sudo（root）：在系统级目录下（/usr/lib/），所有用户可访问


## 外设控制
python3-libgpiod ：标准 GPIO libgpiod 库的 python 版本，只支持控制 IO 输入输出。
python-periphery(帕瑞佛瑞) 支持 GPIO、 PWM、 I2C、 SPI、 UART 等多种接口的基础控制
Adafruit Blinka(“艾达富特 布林卡”)：支持 GPIO、 PWM、 I2C、 SPI、 UART 等，还带有一些常用传感器、 OLED
屏的应用示例。
### spi
python3 -c "from periphery import SPI; print(dir(SPI))" 
这个命令的作用就是**列出 `periphery.SPI` 类定义的所有属性（Attributes）和方法（Methods）**。
具体解释如下：
1.  **`from periphery import SPI`**：从 `periphery` 库中导入 `SPI` 类。
2.  **`dir(SPI)`**：这是 Python 的内置函数。当它作用于一个类或实例时，会返回该对象所有有效的属性名称列表（包括继承自父类的属性、内部私有成员以及魔术方法）。
3.  **`-c`**：表示在命令行执行后面引号内的整个字符串作为 Python 代码。

### 您看到的输出中主要分为几类：
*   **普通方法**：如 `transfer`, `close`。
*   **公共属性**：如 `max_speed`, `mode`, `bit_order`。
*   **私有/内部方法**：以 `_` 开头的，如 `_set_max_speed`, `_set_mode`（这些通常是库内部逻辑使用的，开发者应直接操作不带下画线的属性）。
*   **魔术方法**：以 `__` 开头的，如 `__init__`, `__enter__`, `__exit__`（用于支持 `with` 语句等语法）。

所以，`dir()` 是调试 Python 库（尤其是文档不全或版本差异时）最快、最直接的手段。


## io
```c
import gpiod
chip0 = gpiod.Chip("0", gpiod.Chip.OPEN_BY_NUMBER) 
gpio0_c0 = chip0.get_line(16)
gpio0_c0.request(consumer="gpio", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
gpio0_c0.set_value(1)
```
字符串 "0"：代表打开系统中编号为 0 的控制器

## 语法
### 装饰器
它的核心作用是：在不改变原函数代码的情况下，给函数增加额外的功能
@ 符号是什么？
它是 Python 的“语法糖”。写了 @log_decorator，等于告诉 Python：
“嘿，执行 worker() 之前，先把它丢进 log_decorator 盒子里包装一下再取出来用。”
为什么要嵌套一个 wrapper 函数？
因为装饰器必须返回一个可执行的对象。wrapper（包装纸）就是那个包裹了原函数的新函数
```c
def log_decorator(func):
    def wrapper():
        print("--- 开始打卡 ---")  # 额外功能：打卡
        func()                  # 执行原本的活儿
        print("--- 工作结束 ---")  # 额外功能：记录结束
    return wrapper

# 2. 使用装饰器（用 @ 符号）
@log_decorator
def worker():
    print("正在搬砖...")

# 3. 调用
worker()
```

## 运算符&变量

在 Python 中，or 运算符有一个特性：它会返回第一个为“真”的值

### 不可变(一旦创建，其值就不能改变。如果尝试修改，Python 会在内存中创建一个新对象，并将变量指向这个新地址。)
布尔型 (Boolean)：只有两个值：True 和 False。
容器型 (Collection)：
元组 (Tuple): (1, 2, 3)（不可变有序）

### 可变
字典 (Dictionary): {"key": "value"}
列表 (List): [1, 2, 3]（可变有序）
#### 无序 元素在容器里的位置是随机的（由哈希算法决定），你不能指望它按你放入的顺序排列，也不能使用下标访问。
集合 (Set): {1, 2, 3}（无序且唯一）

## 构造函数

核心三要素
A) self 参数
self 必须是第一个参数。
它代表当前对象本身。通过 self，你才能在对象内部读写属性。
在调用类时，你不需要给 self 传值，Python 会自动帮你传入。
B) 属性初始化 (Initialization)
构造函数的主要任务是给对象赋初值。
如果没有 __init__，对象创建后就是一个“空壳子”，通常需要手动给它加属性（这很麻烦且不推荐）。
C) 返回值限制
__init__ 不能有返回值（即不能有 return 语句，或者只能 return None）。
它的责任是配置对象，而不是产生计算结果

### 父类构造函数

1. 属性继承)：如果父类在 __init__ 中定义了一些属性（如 self.name, self.age），子类如果不显式调用 super().__init__()，它将无法自动获得这些属性。

2. 代码复用)：如果你在父类中写了一些复杂的初始化逻辑（如打开数据库连接、校验参数），子类可以直接利用这些逻辑，而不需要重新写一遍

3. 调用父类的构造函数 (super())
如果你写了一个继承类，必须调用父类的 __init__ 才能继承父类的初始化逻辑：写法)super().__init__(属性) 

4. __new__ 与 __init__ 的区别
__new__：它是真正的“构造者”，负责创建并返回一个对象实例。
__init__：它是“初始化者”，负责对 __new__ 创建出的对象进行配置。
```c
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(HalMeterControl, cls).__new__(cls)
            cls._instance._initialized = False#为下一步的 __init__做准备
        return cls._instance
```
cls是类本身


## 原子化检查与创建（Atomic Check-and-Create）。
_lock = threading.Lock()  线程的互斥锁
进入 with 块前：自动调用 cls._lock.acquire()（尝试拿钥匙开门）。如果门被别人反锁了，当线程会在这里原地等待。
退出 with 块后（不管是正常运行完，还是中间出错了抛异常）：自动调用 cls._lock.release()（把钥匙还回去，让排队的人进来）

## ModuleNotFoundError: No module named 'xxx' 
Python 查找模块 (import xxx) 时，默认只在当前运行文件的目录和系统库路径下寻找

## Eventlet
Eventlet 是 Python 中一个非常著名的高并发网络库。它的核心目标是：让开发者用写“同步代码”（简单直观）的方式，实现“异步程序”（高性能、高并发）的效果。
1. 核心技术：协程 (Coroutines) 与 Greenlet
Eventlet 不使用操作系统的“重量级”线程，而是使用**“轻量级”协程**（在 Python 中叫 Greenlet）。

传统线程：开 1000 个线程可能会吃掉几 GB 内存，且 CPU 在线程间切换（Context Switch）开销巨大。
Eventlet 协程：开 10000 个协程可能只占用几十 MB 内存。协程是在同一个线程里运行的，由 Eventlet 自动调度。
2. 秘密武器：Monkey Patching (猴子补丁)
这是 Eventlet 最神奇也最“暴力”的地方。当你调用 eventlet.monkey_patch() 时，它会悄悄替换 Python 标准库的功能：

它把原生的 socket 换成自己的 eventlet.socket。
它把 time.sleep 换成自己的非阻塞版本。
结果：你写的 time.sleep(1) 看起来是程序停了 1 秒，但实际上 Eventlet 在这 1 秒内已经去处理了成百上千个其他的网络请求
全局生效：monkey_patch() 必须在程序的最早期（任何其他库加载之前）执行，才能成功拦截所有的网络和线程操作。
Socket.IO 要求：当你调用 socketio.run 时，Socket.IO 会检查当前的并发环境。如果检测到 eventlet 已经运行了 monkey_patch，它就会自动切换到高并发模式。

## 权限
1. cd到目录

2. 将数据库文件的所有者改为当前的 cat 用户
sudo chown cat:cat gcv5_jobs.db*

3. 赋予读写权限
sudo chmod 666 gcv5_jobs.db*

4. 顺便修复日志目录的权限（防止程序因无法写日志而崩溃）
sudo chown -R cat:cat logs/
sudo chmod -R 777 logs/