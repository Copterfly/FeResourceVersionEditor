# python3实现的前端资源文件(js/css)版本号修改器软件

github: https://github.com/Copterfly/FeResourceVersionEditor

具体作用和详情介绍请移步本人博客： http://www.copterfly.cn/server-side/python/feResourceVersionEditor.html

## 简介

本软件可批量修改前端资源文件(css/js)的版本号。

本软件诞生初衷为提高前端工作效率，防止手动修改出错，解放生产力。

本软件只适用于64位 windows 操作系统，32位应该打不开。（如果你把代码拿到32位系统下打包，那32位也可以正常使用）

本软件只适用于 `ABC项目`，请勿用在其它项目上。

本软件为绿色软件，无毒无害，解压即可使用（如某数字软件问东问西，点允许运行即可）。

本软件 console(CMD) 版本诞生于 2016-1-18，GUI 版本发布于 2018-1-19。

## 工作原理

在修改资源文件前，给所有资源文件生成快照，修改文件后，运行本软件，检测被修改过的文件，到模板文件目录中查找其路径，匹配并替换版本号为当前时间。

更新版本号后，会自动或可手动重新生成快照，如此循环。

## 如何使用

### 文件目录说明：

│  help.chm ---------- 软件的帮助文件（教程），这里实际上用 jQuery 手册代替
│  icon.ico ---------- 软件的图标
│  app.py ------------ 软件 GUI 主程序
│  versionAction.py -- 软件实现替换等各种功能的程序
│  lib.py ------------ 软件函数库
│  setup.py ---------- 打包程序：py2exe 打包 python 程序为 exe 可执行文件

python 环境下体验和测试：拉取项目文件后，到当前目录运行 GUI 主程序即可。如： `python app.py`

(未完待续)
