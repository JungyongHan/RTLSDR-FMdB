import sys, os
from PyQt5.QtWidgets import * 
from PyQt5 import uic 
from PyQt5.QtCore import QObject, pyqtSignal
ui_path = os.path.dirname(os.path.abspath(__file__))
form_class = uic.loadUiType(os.path.join(ui_path, "ui/dialog.ui"))[0]

class Window(QDialog, form_class):
    def __init__(self, originvalue = '', tooltip = ''):
        super().__init__()
        self.setupUi(self)
        self.__oringvalue = str(originvalue)
        self.setWindowTitle("입력하기")
        for i in range(11):
            btn = getattr(self, "BTN_" + str(i))
            btn.clicked.connect(self.inputtext)
        self.BTN_CLEAR.clicked.connect(self.clear)
        self.BTN_BACK.clicked.connect(self.backspace)
        self.lineEdit.setText(str(self.__oringvalue))
        self.tooltip.setText(tooltip)

    def clear(self):
        self.lineEdit.setText('')

    def backspace(self):
        buff = str(self.lineEdit.text())[:-1]
        self.lineEdit.setText(buff)

    def inputtext(self):
        text = self.sender().text()
        buff = str(self.lineEdit.text()) + text
        self.lineEdit.setText(buff)

    def accept(self):
        self.hide()
    
    def reject(self):
        self.lineEdit.setText(self.__oringvalue)
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    app.exec_()