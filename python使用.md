





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


# 原子化检查与创建（Atomic Check-and-Create）。
_lock = threading.Lock()  线程的互斥锁
进入 with 块前：自动调用 cls._lock.acquire()（尝试拿钥匙开门）。如果门被别人反锁了，当线程会在这里原地等待。
退出 with 块后（不管是正常运行完，还是中间出错了抛异常）：自动调用 cls._lock.release()（把钥匙还回去，让排队的人进来）