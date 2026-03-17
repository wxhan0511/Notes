Flask 是一个用 Python 编写的轻量级 Web 应用框架

定位： Flask 通过 __name__ 知道 app.py 放在 /my_project 这个文件夹里。
自动关联： 知道了这个位置后，Flask 就会自动推断出：
HTML 模板一定在 /my_project/templates。
图片和 CSS 一定在 /my_project/static


## 抓取前端发送给后端的这些 JSON 数据包（HTTP 请求）

1)在浏览器（Chrome/Edge）中按 F12 或右键“检查”。
2)切换到 Network (网络) 标签页。

![alt text](web应用/image1.png)

wireshark
http.request.method == "POST" && tcp.port == 5000


## 流程解析

### read power voltage
![alt text](web应用/image2.png)
solo 指的是单节点控制页面（Solo Mode），即系统的主要操作入口。
在 routes.py 中搜索 @app.route("/solo")。
@api_bp.route("/power/read", methods=["POST"])


## 蓝图教程

蓝图的作用：给不同的功能小组（如 API 组、用户组、静态页面组）分配独立的办公室（文件），最后再由前台（app.py）统一登记。

### 1. 蓝图的定义

创建蓝图对象
'api': 蓝图的名字（用于内部通过 url_for 查找）
__name__: 确定蓝图所在的位置，方便查找 templates 和 static 文件夹命名,空间隔离,如果你有多个蓝图，它们可以有同名的函数而互不干扰：
api_bp = Blueprint('api', __name__)

### 2. 在蓝图上“贴标签” (定义路由)

你不再使用 @app.route，而是使用 @api_bp.route。这意味着这些路径现在属于这个“小组”：
```python
@api_bp.route("/solo")
def solo_node():
    return render_template("index.html")

@api_bp.route("/power/set", methods=["POST"])
def power_set():
    # ... 设置电压的逻辑
    return jsonify({"success": True})
```
### 3. 注册蓝图 (核心，决定了网址长什么样)
蓝图定义好了，但 Flask 还不知道它的存在。你必须在创建 App 的地方（通常是 app.py）注册它。
```python
from web.routes import api_bp
app.register_blueprint(api_bp)
```
结果：网址直接对应。@api_bp.route("/solo") 
http://localhost:5000/solo。

## return render_template("index.html")
这是最关键的一步，它像是一条链条的开头，触发了后续所有的硬件操作：

加载 HTML：服务器从 index.html 读取内容并发送给浏览器。这个 HTML 文件定义了你看到的电源控制按钮、仪表盘布局等界面。
触发静态资源加载：
浏览器解析 index.html 时，会发现里面引用了 script.js。
一旦 script.js 加载成功，它就会开始执行你在前面抓包看到的那些 power/read、status.get 等 API 请求。
