import sys, os
from PyQt5.QtWidgets import * 
from PyQt5 import uic 
from PyQt5.QtCore import QObject, pyqtSignal
import qt_dialog
ui_path = os.path.dirname(os.path.abspath(__file__))
form_class = uic.loadUiType(os.path.join(ui_path, "ui/freqsetting.ui"))[0]

class Window(QWidget, form_class):
    subsignel = pyqtSignal(object)
    #-- freqs
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("주파수 설정")
        self.freqs = []
        #-- btn connect
        for i in range(1, 7):
            btn = getattr(self, "btn_" + str(i))
            btn.clicked.connect(self.freqsetting)
        self.btn_callback.clicked.connect(self.btn_clicked)

    
    def freqtextchg(self):
        for i in range(1, 7):
            btn = getattr(self, "btn_" + str(i))
            if self.freqs[i-1]['freq'] != 0:
                btn.setText(str(self.freqs[i-1]['freq']) + 'Mhz')
            else:
                btn.setText('변경하기')

    def freqsetting(self):
        btn = self.sender()
        name = int(str(btn.objectName()).replace('btn_', '')) - 1
        dlg = qt_dialog.Window(originvalue = self.freqs[name]['freq'], tooltip = '단위는 Mhz 입니다.')
        dlg.exec_()
        try:
            self.freqs[name]['freq'] = float(dlg.lineEdit.text())
            self.subsignel.emit('freq')
        except Exception as ex:
            print("잘못된 입력형태", ex)
        self.freqtextchg()

    def btn_clicked(self):
        self.subsignel.emit('12')
        self.hide()