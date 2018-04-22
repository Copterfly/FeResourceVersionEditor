# -*- coding: utf-8 -*-
'''
python3

前端资源版本号修改器 css/js
------------------------
@Author: Copterfly
@Create: 2016-01-18 星期一
@Update: 2016-02-24 星期三
@为GUI重构: 2018-01-12 星期五
------------------------
原理：
1、记录网站中所有的css/js文件的快照，即修改时间和md5
2、编辑过文件后，遍历快照中的文件，找到被修改的文件
3、在 cshtml 中查找是否引用了被修改的文件，替换为新的版本号（操作时的时间）
4、提交git
5、拉取后（有需要的话），执行步骤1，如此类推。
------------------------
'''
import string, os, re, datetime, time, lib, codecs, json

class VersionAction:
    def __init__(self):
        #self.regexp_ignore_dirs = r'(\\C1\\|\\H2\\|\\L2\\)' # 手机端无用的模板目录，暂时排除
        self.dataDir = lib.cur_dir + os.sep + 'data' + os.sep
        self.file_resource_list = self.dataDir + 'resource_list.txt' # 资源(css/js)记录文件
        self.file_replace_record = self.dataDir + 'replace_record.txt' # 更新记录
        self.file_config = self.dataDir + 'config.ini' # 配置文件
        self.config = {
            # 默认配置
            #show : 1/0 是否显示到设置界面
            #editable : 1/0 是否可编辑
            #required : 1/0 是否必填项
            'project_web_root' : { # 目前只有此项是提供编辑的，也是必需的。其他项先写死。
                'sort': 0, # 排序
                'show'     : 1,
                'editable' : 1,
                'required' : 1,
                'name'     : 'web根目录',
                'desc'     : 'ABC项目路径下的web根目录，如：D:\Projects\SkyMall\Maticsoft.Web，模板和资源文件必须位于此目录下',
                #'value'    : 'D:\Projects\SkyMall-version\Maticsoft.Web'
                'value'    : ''
            },
            'resource_dirs' : {
                'sort': 1,
                'show'     : 1,
                'editable' : 0,
                'required' : 0,
                'name'     : '资源文件目录',
                'desc'     : '要查找的资源文件(.js/.css)可能存在的目录，基于web根目录。填写后可加快查找速度。',
                'value'    : ['Areas', 'Scripts', 'css']
            },
            'template_dir' : {
                'sort': 2,
                'show'     : 1,
                'editable' : 0,
                'required' : 0,
                'name'     : '模板文件目录',
                'desc'     : '模板文件(.cshtml等)目录，基于web根目录。填写后可加快查找速度。',
                'value'    : 'Areas' # 暂时写死一个
            },
            'resource_types' : {
                'sort': 3,
                'show'     : 1,
                'editable' : 0,
                'required' : 0,
                'name'     : '资源文件类型',
                'desc'     : '资源文件类型',
                'value'    : ['.css', '.js']
            },
            'template_types' : {
                'sort': 4,
                'show'     : 1,
                'editable' : 0,
                'required' : 0,
                'name'     : '模板文件类型',
                'desc'     : '模板文件类型',
                'value'    : ['.cshtml']
            }
        }
        self.str_content = r'/CONTENT/'
        self.version_str = r'?v='
        self.resource_list_final_modified_time = ''
        self.resource_list_final_modified_time_format = '%Y-%m-%d %H:%M:%S (%A)'
        self.template_dir = '' # .cshtml 模板目录
        self.resource_dirs = [] # 资源文件所在目录
        self.resource_types   = self.config['resource_types']['value']
        self.template_types = self.config['template_types']['value']
        self.resource_list_recorded = [] # 读取之前记录的资源文件数组
        self.resource_list_modified = [] # 被修改过的资源文件数组
        self.errorLines_replacement = [] # 出错的情况，收集起来
        self.init()
    def init(self):
        self.prepare()
    def prepare(self):
        # 第一次打开时初始化
        # 数据设置目录不存在则创建
        if not os.path.exists(self.dataDir):
            os.mkdir(self.dataDir)
        # 资源快照记录文件最新生成时间
        if os.path.isfile(self.file_resource_list):
            modified_time = int(os.path.getmtime(self.file_resource_list))
            self.resource_list_final_modified_time = time.strftime(self.resource_list_final_modified_time_format, time.localtime(modified_time))
        '''else:
            lib.write_file(self.file_resource_list, '')
            #print(self.file_resource_list, '创建成功')'''
        # 读取配置文件
        if os.path.isfile(self.file_config):
            config = lib.read_file(self.file_config)
            self.config = json.loads(config) # 读取配置
        # 创建配置文件
        else:
            self.action_update_file_config()
        # 检查 web 根目录是否填写正确，决定后面的操作
        check = self.checkConfig_webroot()
        if check['code'] > 0:
            #print(check['msg'])
            return False
        self.action_build_dirs_path()
        #print(template_dir)
        #print(self.resource_dirs)

    # 更新配置文件(配置的变量 self.config 要先更新)
    def action_update_file_config(self):
        lib.write_file(self.file_config, json.dumps(self.config)) # 写入配置
        #print(self.file_config, '更新配置文件成功')
    # 检查配置项 webroot 是否正确(软件启动后及执行修改操作前都要在 app.py 主动执行一次)
    def checkConfig_webroot(self):
        if self.config['project_web_root']['value'] == '':
            return lib.returnMsg(1, '请先到“设置”页去设置：项目的web根目录')
        return lib.returnMsg(0)
    # 拼出各种需要的目录变量 (软件启动后及设置成功后都要在 app.py 主动执行一次)
    def action_build_dirs_path(self):
        # cshtml 目录
        self.template_dir = self.config['project_web_root']['value'] + os.sep + self.config['template_dir']['value']
        # 资源文件所在目录
        #self.resource_dirs = (r'D:\Projects\SkyMall\Maticsoft.Web\Areas', r'D:\Projects\SkyMall\Maticsoft.Web\Scripts', r'D:\Projects\SkyMall\Maticsoft.Web\css')
        project_web_root = self.config['project_web_root']['value']
        for item in self.config['resource_dirs']['value']:
            self.resource_dirs.append(project_web_root + os.sep + str(item))
    
    # 创建资源文件快照，生成记录文件

    # 检查资源文件 # type: record 记录资源文件快照/check 检查资源文件是否被修改过
    def action_check_resource_files(self, type):
        check = self.checkConfig_webroot()
        if check['code'] > 0:
            return check
        elif not os.path.isfile(self.file_resource_list):
            if type == 'check':
                return lib.returnMsg(2, '请先执行生成资源文件快照操作')

        self.resource_get_modified_list(type)
        # 写入记录文件
        if type == 'record':
            return self.action_save_resource_record(self.resource_list_for_recording)
            '''content = lib.line_sep.join(self.resource_list_for_recording) + '\n'
            lib.write_file(self.file_resource_list, content)
            return lib.returnMsg(0, '生成资源文件快照成功，文件总数：' + str(len(self.resource_list_for_recording)))'''
        # 查找引用了资源文件的cshtml文件
        elif type == 'check':
            modifiedCount = len(self.resource_list_modified)
            if modifiedCount > 0:
                code = 0
                msg = '被修改过的资源文件数：%d' % modifiedCount
            else:
                code = 0
                msg = '没有被修改过的资源文件'
            return lib.returnMsg(code, msg, self.resource_list_modified)
        else:
            pass
    '''
    # 执行修改版本号动作 resource_list 需要传进来(这一步没用了，改为在GUI部分操作，以便即时输出替换结果)
    def action_modifyVersion_all(self, resource_list):
        # 在模板文件中查找引用了修改过的资源文件
        self.version_time = datetime.datetime.now().strftime('%Y%m%d-%H%M') # 版本号如：2016216-1802 完整： %Y-%m-%d %H:%M:%S
        for file in resource_list:
            self.modifyVersion(file)
    '''
    # 判断引用资源的cshtml文件所在目录，以加快查找速度，以及省去处理 ViewBag.themeName 的麻烦 (一次处理一个资源文件)
    @lib.MuteStdout(True)
    def action_modifyVersion(self, file, version_time):
        self.version_time = version_time
        ''' 这两个匹配用来确定具体的模板目录，以加快查找速度，但是也会导致跨目录的引用不会被匹配到。
            比如这种情况：
            D:\Projects\SkyMall\Maticsoft.Web\Areas\MSupplier\Themes\M1\Views\Order\Index.cshtml。
            引用了：
            D:\Projects\SkyMall\Maticsoft.Web\Areas\MShop\Themes\H1\Content\js\index.js
        '''
        regexp_dir = r'\\Areas\\(.+)\\Themes\\(.+)\\Content' # 资源文件在某个模板目录的情况
        regexp_dir2 = r'\\Areas\\(.+)\\Shared' # 资源文件在某个 area 公用目录(如：MShop)的情况
        match = re.search(regexp_dir, file, re.I)
        match2 = re.search(regexp_dir2, file, re.I)
        if match:
            #print(match.group())  # eg: \Areas\MShop\Themes\H1\Content
            #print(match.group(1)) # eg: MShop
            #print(match.group(2)) # eg: H1
            theme_name = match.group(2)
            # 拼出模板目录 dir
            # D:\Projects\SkyMall\Maticsoft.Web\Areas\Supplier\Themes\M1\Content\js\xxx.js
            # 变为
            # D:\Projects\SkyMall\Maticsoft.Web\Areas\Supplier\Themes\M1\Views
            dir = re.sub(r'Content.+$', 'Views', file)
            src = file.split(theme_name)[1] # 取得: \Content\js\xxx.js
        elif match2:
            #area = match2.group(1)
            dir = re.sub(r'Shared.+$', 'Themes', file)
            src = file.split('Maticsoft.Web')[1]
        else: # 例如：/css/xx.css 或者 /Scripts/xxx/xxx.js
            dir = self.template_dir
            src = file.split('Maticsoft.Web')[1]
        src = src.replace(os.sep, '/') # 反斜杠转成: /Content/js/xxx.js

        print(lib.hr_line_1)
        #print('资源文件:', src)
        print('资源文件:', file)
        print('模板目录:', dir)
        print(lib.hr_line_2)

        self.modify_walk_dir(dir, src)
        
    # 在模板文件中查找引用了修改过的资源文件
    def modify_walk_dir(self, template_dir, resource_src):
        # 分别返回 1.父目录 2.此目录下直接文件夹名字（不含路径） 3.所有文件名字
        for parent_path, sub_dirs, files in os.walk(template_dir):
            for name in files:
                ext = os.path.splitext(name)[1]
                if ext in self.template_types: # 如果是 cshtml 文件
                    path = os.path.join(parent_path, name)
                    #if re.search(self.regexp_ignore_dirs, path): # 需要排除的目录(区分大小写) (2018-1-12 星期五 这些目录已经被删除掉了)
                    #    continue
                    lines = []
                    flag_matched = False
                    index = 0
                    errorLines = []
                    with codecs.open(path, 'r+', 'utf_8_sig') as f: # 或 utf-8-sig (UTF-8 with BOM)
                        # 遍历文件的每一行内容
                        for line in f:
                            #if line.find(resource_src) > 0: # 区分大小写
                            if re.search(resource_src, line, re.I): # 不区分大小写
                                # 防止 "/Areas/Shop/Themes/M1/Content/Scripts/Common.js" 与 "/Scripts/Common.js" 匹配
                                if self.str_content in line.upper() and not self.str_content in resource_src.upper():
                                    continue
                                flag_matched = True

                                print('模板文件:', path)
                                print('原内容:', line.strip().strip('\n'))
                                match = re.search(r'(.+)(' + resource_src + r'.*?")(.+)', line, re.I)
                                if match:
                                    #print(match.group(2)) # 取得: /Content/js/xxx.js" 或 /Content/js/xxx.js?v=xxxx"
                                    src_slice = re.sub(r'\?v=(.+)?', '', match.group(2).replace('"', '')) # 去掉后面的双引号和版本号: ?v=xxxx"
                                    src_new = src_slice + self.version_str + self.version_time
                                    line = match.group(1) + src_new + '"' + match.group(3) + '\n'
                                    print('修改为:', line.strip())
                                else:
                                    error = '▇ Error:请检查模板文件第 %d 行代码 ' % (index + 1) # in case: script 标签被换行等不正常书写格式
                                    print(error)
                                    errorLines.append(error + path)
                                    #return False
                                print(lib.hr_line_3)
                            lines.append(line) # 保存每一行
                            index += 1
                        if flag_matched: # 如果匹配到，把修改后的内容写入原文件
                            f.seek(0)
                            f.writelines(lines)
                        if len(errorLines): # 如果的出错的情况，收集起来
                            self.errorLines_replacement += errorLines
        
    # 查找被修改过的资源文件
    # type: record 记录资源文件快照/check 检查资源文件是否被修改过
    def resource_get_modified_list(self, type):
        if os.path.isfile(self.file_resource_list):
            self.resource_list_recorded = [] # 读取之前记录的资源文件数组
            lines = lib.read_file_readlines(self.file_resource_list) # 读取之前记录的资源文件数组
            for line in lines:
                self.resource_list_recorded.append(line.strip('\n')) # 重要！必须要去掉行尾换行符，不然使用这个数组去生成快照记录的话，每次都会在每行下加多一个空行
        self.resource_list_modified = [] # 被修改过的资源文件数组
        self.resource_list_for_recording = [] # 所有资源文件数组(作记录用的)
        #self.modified_resource_file_list = [] # 被修改过的资源文件数组

        #start_time = datetime.datetime.now()
        for index in range(len(self.resource_dirs)):
            self.resource_walk_dir(self.resource_dirs[index], type)
        #end_time = datetime.datetime.now()
        #print('执行完毕，耗时：', end_time - start_time)
    # 遍历 资源文件
    def resource_walk_dir(self, dir, type):
        # 分别返回 1.父目录 2.此目录下直接文件夹名字（不含路径） 3.所有文件名字
        for parent_path, sub_dirs, files in os.walk(dir):
            for name in files:
                ext = os.path.splitext(name)[1] # 扩展名如：.css
                if ext in self.resource_types:
                    path = os.path.join(parent_path, name)
                    # 检查资源文件是否被修改过
                    if type == 'check':
                        self.resource_compare_file(path)
                    # 记录资源文件快照
                    elif type == 'record':
                        row = []
                        modified_time = str(int(os.path.getmtime(path))) # 文件的修改时间
                        md5 = lib.get_md5(path)
                        row.extend([modified_time, md5, path])
                        # 如：修改时间timestamp|md5值|路径
                        # 如：1422951103|2ad01d9fef37c57213f0becf38d0fdb0|D:\Projects\SkyMall\Maticsoft.Web\Scripts\zclip\jquery.zclip.js
                        self.resource_list_for_recording.append(lib.row_sep.join(row))
        
    # 资源文件对比，对比时间和md5，以确定文件是否真的被修改过
    def resource_compare_file(self, path):
        for line in self.resource_list_recorded:
            if line.find(path) > 0:
                row = line.split(lib.row_sep)
                modified_time = int(os.path.getmtime(path))
                if modified_time > int(row[0]): # 如果文件现修改时间晚于原修改时间(不一定是修改过内容，有可能修改过其他文件属性什么的，所以要进一步检查md5)
                    md5 = lib.get_md5(path)
                    if md5 != row[1]: # md5 不一致，确认文件被修改过内容
                        self.resource_list_modified.append(path)
    # 生成资源文件快照
    def action_save_resource_record(self, resource_list, type = 'all'):
        content = lib.line_sep.join(resource_list) + '\n'
        lib.write_file(self.file_resource_list, content)
        #modified_time = int(os.path.getmtime(self.file_resource_list))
        #self.resource_list_final_modified_time = time.strftime(self.resource_list_final_modified_time_format, time.localtime(modified_time))
        self.resource_list_final_modified_time = datetime.datetime.now().strftime(self.resource_list_final_modified_time_format) # 直接取现在时间 %A = Wednesday 英文星期几
        # type == 'all':    手动生成全部
        # type == 'partly': 排除资源文件后局部自动更新
        msg = '%s生成资源文件快照成功！文件总数：%d' % ('(自动)' if type == 'partly' else '', len(resource_list))
        return lib.returnMsg(0, msg, self.resource_list_final_modified_time)
