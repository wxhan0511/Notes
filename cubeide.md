## stm32CubeIDE克隆项目并重命名后xxx.ioc文件打不开
修改ioc的文件名和项目文件名一职，refresh后再打开ioc文件，一切正常
## 修改项目名称
推荐用 CubeIDE 的“重命名”功能修改工程名，避免手动改文件夹名。
如果已手动改名，建议删除工程后，重新用 CubeIDE 导入新文件夹，并检查 .project、.cproject、.mxproject 等文件中的工程名是否与文件夹一致。
确保 .ioc 文件和所有工程配置文件在同一目录下。


Properties”→“C/C++ General”→“Paths and Symbols”，确认新文件路径已包含在 Source Folders 里。

 CubeIDE 的“Help → Manage Embedded Software Packages”里下载 STM32CubeF4 包。