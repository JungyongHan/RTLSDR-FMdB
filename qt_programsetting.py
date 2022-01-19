import sys, os
from PyQt5.QtWidgets import * 
from PyQt5 import uic 
from PyQt5.QtCore import QObject, pyqtSignal
import qt_dialog
ui_path = os.path.dirname(os.path.abspath(__file__))
form_class = uic.loadUiType(os.path.join(ui_path, "ui/prosetting.ui"))[0]

class Window(QWidget, form_class):
    subsignel = pyqtSignal(object)
    #-- gps distance, gps split
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("환경설정")
        self.csvtool = None
        self.btn_0.clicked.connect(self.setDistance)
        self.btn_callback.clicked.connect(self.btn_clicked)
    
    def setDistance(self):
        dlg = qt_dialog.Window(originvalue = self.csvtool.distance_for_calcu, tooltip = '단위는 미터(Meter) 입니다.')
        dlg.exec_()
        try:
            self.csvtool.distance_for_calcu = float(dlg.lineEdit.text())
            self.subsignel.emit('distance')
        except:
            pass

    def btn_clicked(self):
        self.subsignel.emit('12')
        self.hide()