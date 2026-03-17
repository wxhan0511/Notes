Flask 是一个用 Python 编写的轻量级 Web 应用框架

定位： Flask 通过 __name__ 知道 app.py 放在 /my_project 这个文件夹里。
自动关联： 知道了这个位置后，Flask 就会自动推断出：
HTML 模板一定在 /my_project/templates。
图片和 CSS 一定在 /my_project/static