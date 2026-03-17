
## 三种语言分工
HTML 定义了网页的内容
CSS 描述了网页的布局
JavaScript 控制了网页的行为

## html

### 介绍
![alt text](javascript_HTML_CSS\HTML示例.jpg)
-------------------------------------------------------------
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>菜鸟教程(runoob.com)</title>
</head>
<body>
    <h1>我的第一个标题</h1>
    <p>我的第一个段落。</p>
</body>
</html>
-------------------------------------------------------------
<!DOCTYPE html> 声明为 HTML5 文档

<html> 元素是 HTML 页面的根元素   ,如<html lang="zh-CN">：声明文档语言为简体中文

<head> 元素包含了文档的元（meta）数据，
如 <meta charset="utf-8"> 定义网页编码格式为 utf-8。
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title> 元素描述了文档的标题
如<title>GCV5 全景仪表盘 V{{ config.VERSION }}</title>     {{ }} = Flask 模板变量，从后端拿数据 
app = Flask(__name__)
app.config['VERSION'] = '1.0.0'   # 这里就是！

<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
rel="stylesheet"告诉浏览器：这是层叠样式表（CSS），用来美化网页。
{{ ... }}是 Jinja2 模板语法，Flask 专用，用来动态生成路径。
url_for('static', filename='style.css')Flask 内置函数，自动生成正确的静态文件访问路径
<body> 元素包含了可见的页面内容
<h1> 元素定义一个大标题
<p> 元素定义一个段落
注：在浏览器的页面上使用键盘上的 F12 按键开启调试模式，就可以看到组成标签

### 调试
VS Code 可以安装 Live Preview 插件来实时预览编写的代码：

### 语法
#### 链接

anchor
<a href="https://www.runoob.com">这是一个链接</a>

#### 图像
<img src="/images/logo.png" width="258" height="39" />

#### 换行
<br>
Line Break

#### HTML 空元素
没有内容的 HTML 元素被称为空元素。空元素是在开始标签中关闭的。