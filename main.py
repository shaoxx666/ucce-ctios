import sys
from PyQt5.QtWidgets import QMainWindow,QApplication,QWidget,QMessageBox
from PyQt5.QAxContainer import QAxWidget
from gui.Ui_main import Ui_MainWindow
from cisco import server
from core import ws_server
from PyQt5 import QtGui,QtWidgets,QtCore
from PyQt5.QtCore import Qt,QCoreApplication,QLockFile,QSharedMemory
from PyQt5.QtWidgets import QSystemTrayIcon, QAction
from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtNetwork import QLocalSocket,QLocalServer
import test
import ctypes
import logging
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

class MyMainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self,parent =None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                event.ignore()
                self.hide()
                return
        super(MyMainWindow, self).changeEvent(event)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.systemTrayIcon.showMessage('Running', 'Running in the background.')

if __name__ == "__main__":
    #logging.info('----run-----')
    #logging.basicConfig(filename=(r'D:\logs\ucce.log'), level=logging.DEBUG, format=LOG_FORMAT)
    app = QApplication(sys.argv)
    try:
        #LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        #logging.basicConfig(filename=r'D:\\log\\ucce.log', level=logging.DEBUG, format=LOG_FORMAT)
        share = QSharedMemory()
        share.setKey("ucce_ctios_gsd")
        if share.attach():
            msg_box = QMessageBox()
            msg_box.setWindowTitle("提示")
            msg_box.setText("软件已在运行!")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.addButton("确定", QMessageBox.YesRole)
            msg_box.exec()
            sys.exit(-1)
        share.create(1)
    except Exception as ex:
        sys.exit(-1)

    ''' app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show() '''
    
    app.setWindowIcon(QIcon(':/cisco.ico'))
    app.setQuitOnLastWindowClosed(False)
    

    myWin = MyMainWindow()
    myWin.setWindowTitle("UCCE CTIOS (V1.1.0)")
    myWin.setWindowFlags(Qt.WindowMinimizeButtonHint)
    #cisco object
    cisco = server.new_cisco_instance(myWin)
    #cisco.reloadactive()

    
    wserver = ws_server.new_web_instance(port=61002,uimain=myWin)
    wserver.start_server()

    
    #myWin.show()
    myWin.hide()
    
    # -------------------- 托盘开始 ----------
    # 在系统托盘处显示图标
    w= myWin
    tp = QSystemTrayIcon(w)
    tp.setIcon(QIcon(':/cisco.ico'))
    # 设置系统托盘图标的菜单
    a1 = QAction('&显示(Show)', triggered=w.show)
    def quitApp():
        w.show()  # w.hide() #隐藏
        re = QMessageBox.question(w, "提示", "退出系统", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if re == QMessageBox.Yes:
            # 关闭窗体程序
            QCoreApplication.instance().quit()
            # 在应用程序全部关闭后，TrayIcon其实还不会自动消失，
            # 直到你的鼠标移动到上面去后，才会消失，
            # 这是个问题，（如同你terminate一些带TrayIcon的应用程序时出现的状况），
            # 这种问题的解决我是通过在程序退出前将其setVisible(False)来完成的。
            tp.setVisible(False)
    a2 = QAction('&退出(Exit)', triggered=quitApp)  # 直接退出可以用qApp.quit
    tpMenu = QMenu()
    tpMenu.addAction(a1)
    tpMenu.addAction(a2)
    tp.setContextMenu(tpMenu)
    # 不调用show不会显示系统托盘
    tp.show()
    # 信息提示
    # 参数1：标题
    # 参数2：内容
    # 参数3：图标（0没有图标 1信息图标 2警告图标 3错误图标），0还是有一个小图标
    tp.showMessage('tp', 'tpContent', icon=0)
    def message():
        print("弹出的信息被点击了")
    tp.messageClicked.connect(message)
    def act(reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2 or reason == 3:
            w.show()
        # print("系统托盘的图标被点击了")
    tp.activated.connect(act)
    # -------------------- 托盘结束 ----------
    #app.exit(app.exec_())
    sys.exit(app.exec_())

    