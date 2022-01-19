import sys, os
from PyQt5.QtWidgets import * 
from PyQt5 import uic 
from PyQt5.QtCore import QObject, pyqtSignal
ui_path = os.path.dirname(os.path.abspath(__file__))
form_class = uic.loadUiType(os.path.join(ui_path, "ui/sdrsetting.ui"))[0]

class Window(QWidget, form_class):
    subsignel = pyqtSignal(object)
    #--gain, samplelate, bandwidth
    def __init__(self, sdr):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("SDR 설정")
        self.sdr = sdr
        self.btn_callback.clicked.connect(self.btn_clicked)
        self.input_gain.setCurrentText(str(sdr.gain))
        print(str(sdr.gain))
        #self.input_samplerate.setCurrentText(str(sdr.sample_rate))
        #self.input_bandwidth.setCurrentText(str(sdr.BandWidth))
    
    def btn_clicked(self):
        self.subsignel.emit([{'name' : 'gain', 'value' : self.input_gain.currentText()}])
        self.hide()