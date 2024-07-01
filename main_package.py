#!/usr/bin/python
# -*- coding: UTF-8 -*-
import win32api
import win32con

class AutoRun():
    def __init__(self):
        name = 'translate'  # 要添加的项值名称
        path = 'D:\\python_work\\work\dist\\translate.exe'  # 要添加的exe路径
        # 注册表项名
        KeyName = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
        # 异常处理
        try:
            key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,  KeyName, 0,  win32con.KEY_ALL_ACCESS)
            win32api.RegSetValueEx(key, name, 0, win32con.REG_SZ, path)
            win32api.RegCloseKey(key)
        except:
            print('添加失败')
        print('添加成功！')
if __name__=='__main__':
     auto=AutoRun();