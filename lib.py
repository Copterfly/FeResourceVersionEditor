# -*- coding: utf-8 -*-

'''
python3
    函数库
    ------------------------
    @Author: Copterlfy
    @Create: 2016-1-18 星期一
    @Update: 2016-1-19 星期二
'''
import os, hashlib

'''
    若装饰器MuteStdout的参数retCache为真，外部调用func()函数时将返回该函数内部print输出的内容(可供屏显)；
    若retCache为假，外部调用func()函数时将返回该函数的返回值(抑制输出)。
    MuteStdout装饰器使用示例如下：

    @MuteStdout(True)
    def Exclaim(): print 'I am proud of myself!'     
    @MuteStdout()
    def Mumble(): print 'I lack confidence...'; return 'sad'     
    print Exclaim(), Exclaim.__name__ #屏显'I am proud of myself! Exclaim'
    print Mumble(), Mumble.__name__  #屏显'sad Mumble'
'''
import sys, io, functools # py3 中没有 cStringIO，用 io 来代替
def MuteStdout(retCache=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            savedStdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                ret = func(*args, **kwargs)
                if retCache == True:
                    ret = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = savedStdout
            return ret
        return wrapper
    return decorator
'''
将函数打包进新开线程，防止卡死UI线程
'''
import threading
def addThread(func, *args):
    t = threading.Thread(target=func, args=args)    
    t.setDaemon(True) # 守护线程
    t.start()    
    # t.join() # 会阻塞，卡死界面

hr_line_1 = '▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇'
hr_line_2 = '================================================================================'
hr_line_3 = '--------------------------------------------------------------------------------'

cur_dir = os.getcwd()
line_sep = '\n'
row_sep = r'|'

# 返回错误信息
def returnMsg(code, msg = '', data = None):
    return { 'code': code, 'msg': msg, 'data': data }

# 整个写文件
def write_file(path, content):
    f = open(path,'w')
    f.write(content)
    f.close()
# 整个读文件
def read_file(path):
    f = open(path,'r')
    content = f.read()
    f.close()
    return content
# 整个读文件 readlines
def read_file_readlines(path):
    f = open(path,'r')
    content = f.readlines()
    f.close()
    return content

# 生成md5
def get_md5(file_path):
    ''' 
        MD5加密算法，返回32位小写16进制符号
        每次读入8k的内容，然后调用 update() 来更新md5。
    '''
    def read_chunks(fh):
        fh.seek(0)
        chunk = fh.read(8096)
        while chunk:
            yield chunk
            chunk = fh.read(8096)
        else: # 最后要将游标放回文件开头
            fh.seek(0)
    m = hashlib.md5()
    if isinstance(file_path, str) and os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            for chunk in read_chunks(fh):
                m.update(chunk)
    # 上传的文件缓存 或 已打开的文件流
    elif file_path.__class__.__name__ in ["StringIO", "StringO"] or isinstance(file_path, file):
        for chunk in read_chunks(file_path):
            m.update(chunk)
    else:
        return ''
    return m.hexdigest()

'''
# 以下 MD5 加密算法，如果要对一个比较大的文件进行校验，将会把文件内容一次读入内存，造成性能上的缺陷。
def get_md5(filename):
    fd = open(filename,'rb')
    fcont = fd.read()
    fd.close()
    fmd5 = hashlib.md5(fcont)
    print(fmd5.hexdigest())

#print(get_md5(resource_list))
'''
    
