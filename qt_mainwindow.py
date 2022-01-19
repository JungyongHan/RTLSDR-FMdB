import sys, os
import qt_spectrum
from PyQt5.QtWidgets import * 
from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal, QEvent

ui_path = os.path.dirname(os.path.abspath(__file__))
form_class = uic.loadUiType(os.path.join(ui_path, "ui/mainwindow.ui"))[0]

class Mainwindow(QMainWindow, form_class):
    spectrum = pyqtSignal(object, bool)
    reloading = pyqtSignal(object, object)
    barupdate = pyqtSignal(int)
    gpsupdate = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.win = qt_spectrum.ExMain()
        self.win.notice.connect(self.closed_event)
        #self.pushButton_5.clicked.connect(self.btn_clicked)
        for i in range(0, 6):
            label = getattr(self, 'freq_' + str(i))
            label.installEventFilter(self)
        self.reloading.connect(self.refresh)
        self.barupdate.connect(self.Bar_Update)
        self.gpsupdate.connect(self.gps_refresh)

    def Bar_Update(self, data):
        self.progressBar.setValue(int(data))

    def closed_event(self, data):
        self.spectrum.emit(self.openNum, False)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            print ("The sender is:", source.objectName())
            self.openNum = int(str(source.objectName()).replace('freq_',''))
            self.spectrum.emit(self.openNum, True)
            self.win.show()
        return super(Mainwindow, self).eventFilter(source, event)
    '''
    def btn_clicked(self, event):
        print( self.sender())
        self.win.show()
    '''
    def refresh(self, num, total_data):
        label = getattr(self, "freq_" + str(num))
        if str(type(total_data)) == "<class 'dict'>":
            if total_data['PilotCompare_dB'] < 12:
                font_color = "#F78181"
            else:
                font_color = "#819FF7"
            #<html><head/><body><p><span style=" font-size:22pt;">97.3Mhz </span><span style=" font-size:22pt; font-weight:600; color:#0000ff;">35dB</span></p></body></html>
            text = '<html><head/><body><p><span style=" font-size:22pt;">' + str(total_data['Center_freq']) + '</span><span style="font-size:22pt; font-weight:600; color:' + font_color + ';">' + str(total_data['Correction_dB']) + '</span></p></body></html>'
            label.setText(text)
        else:
            label.setText('None')
    
    def gps_refresh(self, gpsstr):
        self.gps_label.setText(gpsstr)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Mainwindow()
    myWindow.show()
    app.exec_()