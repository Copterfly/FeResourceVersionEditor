# -*- coding: utf-8 -*-
'''
python3

前端资源版本号修改器 GUI 主程序 v1.0
------------------------
@Author: Copterfly
@Create: 2018-1-15 星期一
@Update: 2018-1-18 星期四
'''
#======================
# imports
#======================
import tkinter as tk
import sys, os, re, time, datetime, lib, versionAction
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as msgBox
#===================================================================

class App:
    def __init__(self, root):
        self.root = root
        self.defaultText = '默认文本'
        self.msgBoxTitle = '操作提示'
        self.webRootDirName = 'Maticsoft.Web' # web根目录文件夹名
        self.isLoading = False # 正在执行操作中
        self.initStyles()
        self.init()
    # 
    def init(self):
        self.versionAction = versionAction.VersionAction()
        self.createTabs()
        self.createMenus()
        self.update_resource_list_final_modified_time()
    # Tab Control
    def createTabs(self):
        self.tabControl = tabControl = ttk.Notebook(self.root) # 创建 tabs 面板

        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)
        tab4 = ttk.Frame(tabControl)
        #tab5 = ttk.Frame(tabControl)
        #tab6 = ttk.Frame(tabControl)

        tabControl.add(tab1, text=' 批量更新版本号 ')
        tabControl.add(tab2, text=' 更新记录 ')
        tabControl.add(tab3, text=' 生成资源文件快照 ')
        tabControl.add(tab4, text=' 设置 ')
        #tabControl.add(tab5, text=' 关于软件 ')
        #tabControl.add(tab6, text=' 对照用 ')

        self.createTab1(tab1)
        self.createTab2(tab2)
        self.createTab3(tab3)
        self.createTab4(tab4)
        #self.createTab5(tab5)
        #self.createTab6(tab6)

        tabControl.pack(expand=1, fill='both')

    # tab控件 1
    def createTab1(self, tab):
        tab.grid_columnconfigure(0, weight=1) # 父元素这个设置让 fieldset 可以伸展100%宽度
        #fieldset = ttk.LabelFrame(tab, text='批量替换区')
        areaTop = ttk.Frame(tab, height=40)
        fieldset_resource = ttk.LabelFrame(tab, text='被修改过的资源文件(单击切换选择状态后再操作):')
        areaTop.grid(row=0, column=0, padx=10, pady=(20, 5), sticky = 'wens') # # windows 设为经典主题 pady=(15, 5)，普通主题 pady=(20, 5)
        #fieldset.grid_columnconfigure(1, weight=1, pad=3) # 父元素这个设置让 第几列 可以伸展100%宽度(index=列的索引)
        fieldset_resource.grid(row=1, column=0, ipadx=10, ipady=5, padx=10, pady=10, sticky = 'wens')
        fieldset_resource.grid_columnconfigure(0, weight=1, pad=3)

        # 控件事件

        # 检查被修改过的资源文件
        def action_checkModified():
            return self.versionAction.action_check_resource_files('check')
        # 检查被修改过的资源文件
        def action_btn_checkModified():
            self.disableBtnsFor_checkModified()
            self.emptyResourceList(self.resourceListBox, True)
            result = self.btnAction(self.btn_checkModified, action_checkModified)
            if result['code'] == 0:
                #print('Line:', sys._getframe().f_lineno, result)
                self.resource_list_modified = result['data'] # 被修改过的资源文件数组，数组有可能为空
                self.outputModifiedResourceList(self.resourceListBox, self.resource_list_modified)
            elif result['code'] == 1:
                self.emptyResourceList(self.resourceListBox)
                self.dialog_confirmAction(result['msg'], self.switchToTab_setup)
            elif result['code'] == 2:
                self.emptyResourceList(self.resourceListBox)
                self.dialog_confirmAction(result['msg'], self.switchToTab_snapResource)

        # 控件
        # 检查被修改过的资源文件
        self.btn_checkModified = ttk.Button(areaTop,text='检查被修改过的资源文件', width=25, cursor='hand2', takefocus = 0, command = action_btn_checkModified) # cursor='hand2' 相当于 CSS 的 pointer
        self.label_resource_list_final_modified_time = ttk.Label(areaTop,text = '--', style = 'tipsInfo.TLabel')

        # 控件位置
        self.btn_checkModified.grid(row=0)
        self.label_resource_list_final_modified_time.grid(row=0, column = 1, padx = 10)

        ##### fieldset_resource #####
        # 全选、全不选
        def action_btn_selectAll():
            self.resourceListBox.selection_set(0, 'end')
            self.setBtnsStatusFor_select(True)
            self.resourceListBoxSelection = self.resourceListBox.curselection()
        def action_btn_selectNone():
            self.resourceListBox.selection_clear(0, 'end')
            self.setBtnsStatusFor_select(False)
        # 单选、单不选
        def resourceListBoxSelect(event):
            self.resourceListBoxSelection = self.resourceListBox.curselection() # 返回 tuple, 如: (0,),  (0, 2, 8)
            #print("clicked at", event.x, event.y)
            #print(len(self.resourceListBoxSelection), self.resourceListBoxSelection)
            if len(self.resourceListBoxSelection):
                self.setBtnsStatusFor_select(True)
            else:
                self.setBtnsStatusFor_select(False)
        
        # 选择栏
        rowSelect = ttk.Frame(fieldset_resource, height = 40)
        txt_select = ttk.Label(rowSelect, justify='left', text = '选择：')
        self.btn_selectAll = ttk.Button(rowSelect,text='全选', width=10, cursor='hand2', command = action_btn_selectAll) # cursor='hand2' 相当于 CSS 的 pointer
        self.btn_selectNone = ttk.Button(rowSelect,text='全不选', width=10, cursor='hand2', command = action_btn_selectNone) # cursor='hand2' 相当于 CSS 的 pointer
        # 列表区
        yScrollbar = tk.Scrollbar(fieldset_resource) # 滚动条
        # windows 设为经典主题 height = 24 才刚刚好，普通主题 22
        self.resourceListBox = tk.Listbox(fieldset_resource, yscrollcommand = yScrollbar.set, selectmode = 'multiple', borderwidth = 0, height = 22, font = ('', 9), activestyle = 'none', fg = '#2B54D0', selectforeground = '#FFF', selectbackground = '#0A246A')  
        #self.resourceListBox.bind('<Button-1>', resourceListBoxSelect) # 不行，抓获的结果是点击前的
        self.resourceListBox.bind('<<ListboxSelect>>', resourceListBoxSelect) # 虚拟事件，当选择项变化时触发
        #for item in ['python', 'tkinter', 'widget++']:
        #    self.resourceListBox.insert('end', item)

        # 操作栏
        rowAction = ttk.Frame(fieldset_resource, height = 40)
        txt_selecttion = ttk.Label(rowAction, justify='left', text = '选中项：')
        self.btn_updateVersion = ttk.Button(rowAction,text='批量更新版本号', width=18, cursor='hand2', command = self.action_btn_updateVersion) # cursor='hand2' 相当于 CSS 的 pointer
        self.btn_setNotModified = ttk.Button(rowAction,text='设为非修改状态', width=18, cursor='hand2', command = self.action_btn_setNotModified) # cursor='hand2' 相当于 CSS 的 pointer

        # 布局
        rowSelect.grid(row=0, column=0, sticky = 'w', padx = (10, 0), pady = (10, 2))
        txt_select.grid(row=0, column=0, sticky = 'w')
        self.btn_selectAll.grid(row=0, column=1, sticky = 'w', padx = (3, 0))
        self.btn_selectNone.grid(row=0, column=2, sticky = 'w', padx = (3, 0))

        self.resourceListBox.grid(row=1, column=0, sticky = 'we', padx = (10, 0), pady = 5)
        yScrollbar.grid(row=1, column=1, sticky = 'sn', padx = (0, 10), pady = 5)
        yScrollbar.config(command = self.resourceListBox.yview) # 操作滚动条，listbox 跟着动

        rowAction.grid(row=2, column=0, sticky = 'w', padx = (10, 0), pady = (5, 0))
        txt_selecttion.grid(row=0, column=0, sticky = 'w')
        self.btn_updateVersion.grid(row=0, column=1, sticky = 'w', padx = (3, 0))
        self.btn_setNotModified.grid(row=0, column=2, sticky = 'w', padx = (3, 0))

        self.disableBtnsFor_checkModified()

    # tab控件 2 更新记录
    def createTab2(self, tab):
        tab.grid_columnconfigure(0, weight=1) # 父元素这个设置让 fieldset 可以伸展100%宽度
        fieldset = ttk.LabelFrame(tab, text='最近一次的更新记录')
        fieldset.grid(row=0, column=0, padx=10, pady=10, sticky = 'wens') # 或?: sticky = tk.N + tk.E + tk.S + tk.W
        fieldset.grid_columnconfigure(0, weight=1, pad=3) # 父元素这个设置让 第几列 可以伸展100%宽度(index=列的索引)

        yScrollbar = tk.Scrollbar(fieldset, orient = 'vertical') # 滚动条 垂直
        xScrollbar = tk.Scrollbar(fieldset, orient = 'horizontal') # 滚动条 水平
        self.updateRecordBox = tk.Text(fieldset, height=33, yscrollcommand = yScrollbar.set, xscrollcommand = xScrollbar.set, font = ('', 9), foreground = '#333', padx = 4, wrap = 'none') # none: 强制不换行
        self.updateRecordBox.grid(row=0, sticky = 'we', padx=(10, 0), pady=(10, 0))
        yScrollbar.grid(row=0, column=1, sticky = 'sn', padx = (0, 10), pady = (10, 0))
        xScrollbar.grid(row=1, column=0, sticky = 'we', padx = (10, 0), pady = (0,10))
        yScrollbar.config(command = self.updateRecordBox.yview) # 操作滚动条， updateRecordBox 跟着动
        xScrollbar.config(command = self.updateRecordBox.xview) # 操作滚动条， updateRecordBox 跟着动
        # 如果有更新记录文件的话，读取并显示出来
        if os.path.isfile(self.versionAction.file_replace_record):
            content = lib.read_file(self.versionAction.file_replace_record)
            self.updateRecordBox.insert('end', content)
        self.updateRecordBox.config(state='disabled')
        # INSERT表示在光标位置插入  updateRecordBox.insert(index,string)  index = x.y 的形式,x表示行，y表示列，如：1.0 #向第一行,第一列添加文本
        # END表示在末尾处插入
        '''
        for index in range(500):
            #self.updateRecordBox.insert('end', 'FishC.com!' + lib.line_sep)
            self.updateRecordBox.insert('end', str(index) + lib.line_sep)
            self.updateRecordBox.see('end') # 每插入一条自动滚动到底部
        self.updateRecordBox.config(state='disabled')
        '''

    # tab控件 3 生成资源文件快照
    def createTab3(self, tab):
        tab.grid_columnconfigure(0, weight=1) # 父元素这个设置让 fieldset 可以伸展100%宽度
        '''
        fieldset = ttk.LabelFrame(tab, text='生成资源文件快照')
        fieldset.grid(row=0, column=0, ipadx=10, ipady=10, padx=10, pady=10, sticky = 'wens') # 或?: sticky = tk.N + tk.E + tk.S + tk.W
        fieldset.grid_columnconfigure(1, weight=1, pad=3) # 父元素这个设置让 第几列 可以伸展100%宽度(index=列的索引)
        '''
        areaTop = ttk.Frame(tab)
        areaTop.grid(row=0, column=0, padx=10, pady=(20, 5), sticky = 'wens') # 或?: sticky = tk.N + tk.E + tk.S + tk.W
        areaTop.grid_columnconfigure(1, weight=1, pad=3) # 父元素这个设置让 第几列 可以伸展100%宽度(index=列的索引)

        # 控件事件

        # 生成资源文件快照
        def action_snapResource():
            return self.versionAction.action_check_resource_files('record')
        # 生成资源文件快照
        def action_btn_snapResource():
            result = self.btnAction(btn_snapResource, action_snapResource)
            #print('Line:', sys._getframe().f_lineno, result)
            if result['code'] == 0:
                self.dialog(result['msg'])
                self.update_resource_list_final_modified_time()
            elif result['code'] == 1:
                self.dialog_confirmAction(result['msg'], self.switchToTab_setup)

        # 控件

        # 生成资源文件快照
        btn_snapResource = ttk.Button(areaTop,text='生成全部资源文件快照', width=25, cursor='hand2', takefocus = 0, command = action_btn_snapResource) # cursor='hand2' 相当于 CSS 的 pointer
        #desc = ttk.Label(areaTop, text = '对web根目录下所有资源文件生成快照', style = 'tipsInfo.TLabel')
        #print(desc.winfo_class())
        self.label_resource_list_final_modified_time2 = ttk.Label(areaTop,text = '--', style = 'tipsInfo.TLabel')

        # 控件位置
        btn_snapResource.grid(row=0)
        self.label_resource_list_final_modified_time2.grid(row=0, column = 1, padx = 10, sticky = 'w')
        #desc.grid(row=1)

        # 一次性控制各控件之间的距离
        '''for child in areaTop.winfo_children(): 
            child.grid_configure(sticky = 'w', padx=10, pady=(10, 5))'''
        # 单独控制个别控件之间的距离
        #xxx.grid(column=2,row=1,rowspan=2,padx=6)

    # tab控件 4 设置页
    def createTab4(self, tab):
        tab.grid_columnconfigure(0, weight=1) # 父元素这个设置让 fieldset 可以伸展100%宽度
        fieldset = ttk.LabelFrame(tab, text='设置')
        fieldset.grid(row=0, column=0, ipadx=10, ipady=10, padx=10, pady=10, sticky = 'wens') # 或?: sticky = tk.N + tk.E + tk.S + tk.W
        fieldset.grid_columnconfigure(1, weight=1, pad=3) # 父元素这个设置让 第几列 可以伸展100%宽度(index=列的索引)

        # 控件事件

        # 控件
        items_temp = []
        items = []
        # dict to list
        for item in self.versionAction.config:
            items_temp.append(self.versionAction.config[item])
        for item in items_temp:
            _item = {}
            _item['sort'] = item['sort']
            _item['name'] = item['name']
            _item['label'] = ttk.Label(fieldset, text=item['name'])
            _item['value'] = tk.StringVar()
            if item['editable']:
                _item['entry'] = ttk.Entry(fieldset, takefocus = 0, textvariable = _item['value']) # 在Entry中设定初始值，使用 textvariable 将变量与Entry绑定
                desc = item['desc']
            else:
                _item['entry'] = ttk.Entry(fieldset, takefocus = 0, textvariable = _item['value'], state = 'readonly') # 只读
                desc = '(暂不提供编辑) ' + item['desc']
            _item['value'].set(item['value'])
            _item['desc'] = ttk.Label(fieldset, text = desc, style = 'tipsInfo.TLabel')

            items.append(_item)
        #items.sort(key=lambda k: k['sort'], reverse=True) # 倒序排
        items.sort(key=lambda k: k['sort']) # 顺序排

        # 设置 确定 (只对 web根目录作验证)
        def action_btn_setupOK():
            web_root = items[0]['value'].get()
            web_root_name = items[0]['name']
            if web_root == '':
                self.dialog('%s: 不能为空' % web_root_name, 'warning')
                return False
            if web_root[-1] == '\\': # 后面如果有斜杠结果则去掉
                web_root = web_root[0:-1]
            if not os.path.exists(web_root):
                self.dialog('%s: 文件夹不存在' % web_root_name)
                return False
            elif not os.path.isfile(web_root + os.sep + 'Web.config'):
                self.dialog('%s: 不正确。\n\n请确保您输入的是：\nABC项目路径下的web根目录，如：\nD:\Projects\SkyMall\Maticsoft.Web' % web_root_name)
                return False
            # 更新配置文件
            self.versionAction.config['project_web_root']['value'] = web_root
            self.versionAction.action_update_file_config()
            self.versionAction.action_build_dirs_path()
            self.dialog('设置成功')

        btn_setupOK = ttk.Button(tab,text='确定', width=20, cursor='hand2', command=action_btn_setupOK) # cursor='hand2' 相当于 CSS 的 pointer

        # 控件位置
        for index, item in enumerate(items):
            index *= 2 # 因 desc 要占一行
            item['label'].grid(row=index, column=0, sticky = 'e', padx=(10, 5), pady=(15,4))
            item['entry'].grid(row=index, column=1, sticky = 'we', ipady=3, padx=(0, 10), pady=(15,4))
            item['desc'].grid(row=index+1, column=1, sticky = 'w')
        btn_setupOK.grid(row=1)

    # 跳到tab页 生成资源文件快照
    def switchToTab_snapResource(self):
        self.tabControl.select(2)
    # 跳到tab页 设置
    def switchToTab_setup(self):
        self.tabControl.select(3)
    # 创建顶部菜单
    def createMenus(self):
        menuBar = Menu(self.root)
        self.root.config(menu=menuBar)
        # 菜单组 1
        menuGroup1 = Menu(menuBar, tearoff=0)
        menuGroup1.add_command(label="打开快照所在目录", command=self.menuAction_openSnapDir)
        menuGroup1.add_separator() # 分隔线
        menuGroup1.add_command(label="退出", command=self.quit_confirm)
        # 菜单组 2
        menuGroup2 = Menu(menuBar, tearoff=0)
        menuGroup2.add_command(label="使用教程", command=self.menuAction_help)
        menuGroup2.add_separator() # 分隔线
        menuGroup2.add_command(label="关于软件", command=self.menuAction_about)
        '''
        menuGroup2.add_command(label="通知 Box", command=self._msgBox1)
        menuGroup2.add_command(label="警告 Box", command=self._msgBox2)
        menuGroup2.add_command(label="错误 Box", command=self._msgBox3)
        menuGroup2.add_separator()
        menuGroup2.add_command(label="判断对话框", command=self._msgBox4)
        '''
        # 构建菜单组
        menuBar.add_cascade(label="文件", menu=menuGroup1)
        menuBar.add_cascade(label="帮助", menu=menuGroup2)
    '''# 菜单组 2 的弹窗们
    def _msgBox1(self, msg = '通知：程序运行正常！'):
        msgBox.showinfo('提示', msg)
    def _msgBox2(self):
        msgBox.showwarning('Python Message Warning Box', '警告：程序出现错误，请检查！')
    def _msgBox3(self):
        msgBox.showwarning('Python Message Error Box', '错误：程序出现严重错误，请退出！')
    def _msgBox4(self):
        answer = msgBox.askyesno("Python Message Dual Choice Box", "你喜欢这篇文章吗？\n您的选择是：")
        if answer == True:
            msgBox.showinfo('显示选择结果', '您选择了“是”，谢谢参与！')
        else:
            msgBox.showinfo('显示选择结果', '您选择了“否”，谢谢参与！')
    '''
    # 输出被修改过的资源文件列表到 listbox
    def outputModifiedResourceList(self, listbox, dataList):
        listbox.config(state = 'normal')
        listbox.delete(0, 'end') # 清空原有内容
        re_ext = r'\.(js)$' # 匹配是否js
        if len(dataList):        
            for index, item in enumerate(dataList):
                # D:\Projects\SkyMall-version\Maticsoft.Web\Areas\MShop\Themes\H1\Content\js\global.js
                # 转为
                # /Areas/MShop/Themes/H1/Content/js/global.js
                src = item.split(self.webRootDirName)[1]
                src = ' ' + self.webRootDirName + src.replace(os.sep, '/')
                match = re.search(re_ext, src, re.I)
                '''if match:
                    src = ' .js |' + src
                else:
                    src = ' .css|' + src'''
                listbox.insert('end', src)
                #if index % 2:
                if match:
                    listbox.itemconfig(index, bg = '#FCF2E3')
            self.enableBtn(self.btn_selectAll) # 全选
            self.enableBtn(self.btn_selectNone) # 全不选
        else:
            listbox.insert('end', ' 没有被修改过的资源文件')
            listbox.config(state = 'disabled')
            
    # 清空listbox (是否需要加 loading)
    def emptyResourceList(self, listbox, isAddLoading = False):
        listbox.config(state = 'normal')
        listbox.delete(0, 'end') # 清空原有内容
        if isAddLoading:        
            listbox.insert('end', ' 加载中...')
        listbox.config(state = 'disabled')
    
    # 设置样式
    def initStyles(self):
        s = ttk.Style()
        s.configure('tipsInfo.TLabel', foreground = '#666')
    
    # 简单提示框
    def dialog(self, msg, type = 'info'):
        if type == 'info':
            msgBox.showinfo(self.msgBoxTitle, msg)
        elif type == 'warning':
            msgBox.showwarning(self.msgBoxTitle, msg)
        elif type == 'error':
            msgBox.showerror(self.msgBoxTitle, msg)
    # 确认操作提示框
    def dialog_confirmAction(self, msg, callback):
        answer = msgBox.askokcancel(self.msgBoxTitle, msg) # askyesno
        if answer == True:
            callback();
        #else:
            #msgBox.showinfo('xx', '您选择了“否”')
    # 打开快照所在目录
    def menuAction_openSnapDir(self):
        os.startfile(lib.cur_dir + os.sep + 'data')
    # 打开帮助文件
    def menuAction_help(self):
        os.startfile(lib.cur_dir + os.sep + 'help.chm')
    # 
    def menuAction_about(self):
        msgBox.showinfo('关于软件', 'ABC项目前端资源版本号修改器\n版本: v1.0 (2018-1-19)\n作者: Copterfly')

    # 禁用按钮
    def disableBtn(self, btn):
        btn.config(state = 'disabled')
        #btn.update_idletasks()
    # 启用按钮
    def enableBtn(self, btn):
        btn.config(state = 'normal')
        #btn.update_idletasks()

    # 点击按钮操作，显示 loading 等，执行完操作，返回数据，再把文字改回原来的 # 主要用于需要较长时间的操作
    def btnAction(self, btn, callback):
        originalText = btn.cget('text') # 原按钮文字
        self.disableBtn(btn)
        btn.config(text = '请稍候...')
        btn.update_idletasks()
        result = callback()
        btn.config(state = 'normal')
        self.enableBtn(btn)
        btn.config(text = originalText)
        return result
    # 点击 检查被修改过的资源文件 按钮时，需要禁用的其它按钮
    def disableBtnsFor_checkModified(self):
        self.disableBtn(self.btn_selectAll) # 全选
        self.disableBtn(self.btn_selectNone) # 全不选
        self.disableBtn(self.btn_updateVersion) # 更新版本号
        self.disableBtn(self.btn_setNotModified) # 设为非修改过状态
    # 选择被修改过的资源文件时，需要禁用/启用的操作按钮
    def setBtnsStatusFor_select(self, status = False):
        if status:
            self.enableBtn(self.btn_updateVersion) # 更新版本号
            self.enableBtn(self.btn_setNotModified) # 设为非修改过状态
        else:
            self.disableBtn(self.btn_updateVersion) # 更新版本号
            self.disableBtn(self.btn_setNotModified) # 设为非修改过状态
    # 选中的被修改过的资源文件数组
    def get_resource_list_modified_selected(self):
        arr = []
        for item in self.resourceListBoxSelection:
            arr.append(self.resource_list_modified[item])
        return arr
    # 
    def action_btn_updateVersion(self):
        self.dialog_confirmAction('确定更新选中的资源文件的版本号？', self._action_btn_updateVersion)
    # 
    def _action_btn_updateVersion(self):
        self.tabControl.select(1) # 跳到 更新记录 tab
        lib.addThread(self._action_btn_updateVersion_do)
    # 
    def _action_btn_updateVersion_do(self):
        startTime = datetime.datetime.now()

        version_time = startTime.strftime('%Y%m%d-%H%M') # 版本号如：2016216-1802 完整： %Y-%m-%d %H:%M:%S
        resource_list_modified_selected = self.get_resource_list_modified_selected() # 选中的: 被修改过的资源文件数组

        self.updateRecordBox.config(state='normal')
        self.updateRecordBox.delete(1.0, 'end') # 先清空
        self.versionAction.errorLines_replacement = [] # 出错的情况，收集起来
        for file in resource_list_modified_selected:
            result = self.versionAction.action_modifyVersion(file, version_time)
            self.updateRecordBox.insert('end', result + lib.line_sep)
            self.updateRecordBox.see('end') # 每插入一条自动滚动到底部
        self.updateRecordBox.insert('end', lib.hr_line_1 + lib.line_sep + lib.line_sep)
        self.updateRecordBox.insert('end', '【更新成功，耗时：%s】' % str(datetime.datetime.now() - startTime))
        self.updateRecordBox.insert('end', lib.line_sep + lib.line_sep)
        # 如果有错误信息
        if len(self.versionAction.errorLines_replacement):
            self.updateRecordBox.insert('end', lib.hr_line_1 + lib.line_sep + lib.line_sep)
            self.updateRecordBox.insert('end', '【出错信息】：' + lib.line_sep + lib.line_sep)
            for line in self.versionAction.errorLines_replacement:
                self.updateRecordBox.insert('end', line + lib.line_sep)
            self.updateRecordBox.insert('end', lib.line_sep)
        
        self.updateRecordBox.see('end')
        self.updateRecordBox.config(state='disabled')
        # 取全部内容，更新到记录文件
        lib.write_file(self.versionAction.file_replace_record, self.updateRecordBox.get(1.0, 'end'))
        self._action_btn_setNotModified('所选资源文件版本号更新成功且自动设为非修改状态！') # 自动排除所选资源文件

    # 把选中的文件设为非修改状态 对话框
    def action_btn_setNotModified(self):
        self.dialog_confirmAction('确定把选中的资源文件设为非修改状态？', self._action_btn_setNotModified)

    # 把选中的资源文件设为非修改状态
    def _action_btn_setNotModified(self, msg = '设为非修改状态成功！'):
        resource_list_modified_selected = self.get_resource_list_modified_selected() # 选中的: 被修改过的资源文件数组

        # 在已记录的资源列表中找到被选中的文件
        new_lines = []
        # 每一条如：1422951103|2ad01d9fef37c57213f0becf38d0fdb0|D:\Projects\SkyMall\Maticsoft.Web\Scripts\zclip\jquery.zclip.js
        for line in self.versionAction.resource_list_recorded:
            for path in resource_list_modified_selected:
                if line.find(path) > 0:
                    row = []
                    modified_time = str(int(os.path.getmtime(path))) # 文件的修改时间
                    md5 = lib.get_md5(path)
                    row.extend([modified_time, md5, path])
                    # 如：修改时间timestamp|md5值|路径
                    # 如：1422951103|2ad01d9fef37c57213f0becf38d0fdb0|D:\Projects\SkyMall\Maticsoft.Web\Scripts\zclip\jquery.zclip.js
                    line = lib.row_sep.join(row)
                    break
            new_lines.append(line)
        result = self.versionAction.action_save_resource_record(new_lines, 'partly') # 生成资源文件快照(部分更新)
        #print(result)
        if result['code'] == 0:
           self.dialog(msg + '\n\n' + result['msg'])
           self.update_resource_list_final_modified_time()
           self.btn_checkModified.invoke() # 自动触发按钮： 检查被修改过的资源文件
        elif result['code'] == 1:
            self.dialog_confirmAction(result['msg'], self.switchToTab_setup)

    # 更新资源文件快照生成时间
    def update_resource_list_final_modified_time(self):
        text = '资源文件快照最近生成时间: ' + self.versionAction.resource_list_final_modified_time
        self.label_resource_list_final_modified_time.config(text = text)
        self.label_resource_list_final_modified_time2.config(text = text)
    
    # 窗体的关闭按钮事件
    def quit_confirm(self):
        if self.isLoading:
            if msgBox.askyesno(self.msgBoxTitle, '确定退出软件？您正在执行操作，退出有可能会发生错误。'):
                self._quit()
        else:
            self._quit()
    # Exit GUI cleanly
    def _quit(self):
        self.root.quit()
        self.root.destroy()
'''
-----------------------------------------------
 启动界面
-----------------------------------------------
'''
windowWidth = 800
windowHeight = 500
root = tk.Tk()
root.withdraw() # 创建窗口之后，立即将它隐藏，否则，后面的部件添加和布局过程，都会在屏幕上展现给用户，给用户的感觉就是，窗口在屏幕上乱晃了几下。布局完成后再显示出来。
app = App(root)
root.protocol('WM_DELETE_WINDOW', app.quit_confirm)

root.title('ABC项目前端资源版本号修改器 v1.0') # 窗体标题
#root.geometry('%dx%d' % (windowWidth, windowHeight)) # 指定主框体大小；600x480
root.resizable(0,0) # GUI 框体大小可调性，分别表示x,y方向的可变性；
'''
root.quit() # 退出；
root.update_idletasks()
root.update() # 刷新页面；
'''
# nameEntered.focus() # Place cursor into name Entry 使此控件获得焦点

# Tkinter程序屏幕居中，获取初始化的窗体大小和屏幕大小，再通过计算得到大体值。
#windowWidth = root.winfo_reqwidth() # get current width
#windowHeight = root.winfo_height() # get current height
screenWidth, screenHeight = root.maxsize() # get screen width and height，或者：screenWidth = root.winfo_screenwidth(), screenHeight = root.winfo_screenheight()
layout = '%dx%d+%d+%d' % (windowWidth, windowHeight, (screenWidth-windowWidth)/2, (screenHeight-windowHeight)/2) # 窗口宽、高，左，顶
root.geometry(layout) # 重设 layout
root.deiconify()
root.iconbitmap(r'icon.ico') # 程序图标
root.mainloop()
