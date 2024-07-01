from PyQt5.QtCore import QObject
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class ActiveXExtend(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    # event handler
    def _OnConnectCtiSuccedEvent(self):
        print("receive event")

    #  初始化组件
    def initUI(self):
        #  创建一个LCD屏幕和水平滑块
        lcd = QLCDNumber(self)
        sld = QSlider(Qt.Horizontal, self)
        #  创建一个垂直布局，并将组件添加进去
        vbox = QVBoxLayout()
        vbox.addWidget(lcd)
        vbox.addWidget(sld)
        #  将垂直布局放入窗口
        self.setLayout(vbox)
        #  将sld的值与lcd的屏幕绑定
        sld.valueChanged.connect(lcd.display)
        #  不注释了
        self.setGeometry(300, 300, 300, 250)
        self.setWindowTitle('Signal and slot')

        self.axWidget = QAxWidget("activex")
        self.axWidget.setControl("ax.cti")
        # receive ActiveX event. 
        #self.axWidget.dynamicCall("DisposeControl()")
        #self.axWidget.dynamicCall("InitControl(const QString&,const QString&,const QString&,const QString&,const QString&,const QString&)",self.__host_main, self.__port_main, self.__host_back, self.__port_back, "d:\\log\\", "7001")
        #self.axWidget.OnConnectCtiSuccedEvent.connect(self._OnConnectCtiSuccedEvent)


        self.show()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = ActiveXExtend()
    w.show()
    sys.exit(app.exec_())