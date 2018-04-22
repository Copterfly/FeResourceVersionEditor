# python3
from distutils.core import setup
import py2exe
import sys
 
#this allows to run it with a simple double click. (py文件被 Brackets 关联了，所以还是需要 python 环境运行此脚本)
sys.argv.append('py2exe')

'''
    如果提示：
          2 missing Modules
          ------------------
        ? pywintypes                          imported from -
        ? win32api                            imported from platform, win32evtlogutil
        
        解决方案：把
            D:\Program Files\Anaconda3\Lib\site-packages\win32 下的两个文件复制到 lib 目录:
                pywintypes34.dll
                pythoncom34.dll (不复制这个好像也OK)
            D:\Program Files\Anaconda3\Lib\site-packages\win32\lib
    打包参数：
        bundle_files： 如果要把python编译的所有文件打包到一个exe中，就需要在setup()这个函数中，要设置2个参数：options中的 bundle_files 和 zipfile 。
            其中bundle_files有效值为：
            3 (默认)不打包。
            2 打包，但不打包Python解释器。
            1 打包，包括Python解释器。
'''
options = {
    #'dll_excludes': ['MSVCP90.dll',],  # 这句必须有，不然打包后的程序运行时会报找不到MSVCP90.dll，如果打包过程中找不到这个文件，请安装相应的库
    #'dist_dir': 'dist',
    #'includes': ['sip', 'xxxx'],  # 要包含的其它库文件 # 如果打包文件中有PyQt代码，则这句为必须添加的
    'includes': ['lib', 'versionAction'], # 要包含的其它库文件
    'compressed': 1, # 压缩
    'optimize': 2,
    'ascii': 0,
    'bundle_files': 2, # win7 64位 提示不能用1，只能用2。1表示pyd和dll文件会被打包到exe文件中，且不能从文件系统中加载python模块；值为2表示pyd和dll文件会被打包到exe文件中，但是可以从文件系统中加载python模块
}
 
setup(
    name = 'ABC项目前端资源版本号修改器', # 没用？哪也没显示
    version = '1.0',
    zipfile = None, # 不生成 library.zip 文件
    windows = [{'script': 'app.py', 'icon_resources': [(1, 'icon.ico')] }], # 源文件，程序图标(不需要图标可以这么写: windows = ['calc.py',],)
    #console = [{'script': 'add.py', 'icon_resources': [(1, 'icon.ico')] }], # 源文件，程序图标(不需要图标可以这么写: windows = ['calc.py',],)
    options = { 'py2exe': options }
)

