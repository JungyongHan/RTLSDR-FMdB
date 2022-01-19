#-*- coding:utf-8 -*-
import math
import threading
import queue
import struct
import pyqtgraph as pg
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, Qt, QThread, QTimer
from multiprocessing import Process, Queue
import time, random, os

class ExMain(QWidget):
    sender = pyqtSignal(int, object, object, object)
    notice = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        layout = QGridLayout()
        self.pw1 = pg.PlotWidget(title="IF")
        self.pw2 = pg.PlotWidget(title="MPX")
        self.la1 = QLabel()
        self.la2 = QLabel()
        button = QPushButton(text="out")
        button.clicked.connect(self.__close)

        layout.addWidget(self.pw1, 2, 0, 1, 2)
        layout.addWidget(self.pw2, 2, 3, 1, 2)
        layout.addWidget(self.la1, 1, 0, 1, 3)
        layout.addWidget(button, 1, 4)
        layout.addWidget(self.la2, 0, 0, 1, 5)

        self.sender.connect(self.write)
        self.setLayout(layout)
        self.resize(800, 400)  # x, y, width, height
        
        # self.pw1.setYRange(1, 10)
        # self.pw1.enableAutoScale()
        # self.pw1.enableAutoRange()  # x,y축 모두 autorange
        # self.pw1.enableAutoRange(axis='x', enable=True)
        # self.pw1.enableAutoRange(axis='x')
        # self.pw1.enableAutoRange(axis='y')
        # self.pw1.enableAutoRange(axis='xy')

        # self.pw2.enableAutoRange()
        self.p1 = self.pw1.plot(pen='g')
        self.p2 = self.pw2.plot(pen='r')
        self.p1.setData([1,2,3],[1,2,3])
        self.p1_y_max = 0
        self.p2_y_max = 0
        self.p1_y_min = 0
        self.p2_y_min = 0
        self.__cnt = 0
        self.titletext = ""

        self.setWindowTitle("스펙트럼")
    
    def write(self, plot_N, freqs, power, text):
        changed = False
        max_space = 13
        min_space = 13
        if(plot_N == 1):
            #-- 대충 그래프 그리고, 여백 공간 계산하는 함수
            self.p1.setData(freqs, power)
            center_freq = freqs[int((len(freqs) - 1)/2)]
            self.titletext = "{}Mhz: {}dB".format(round(center_freq, 1), text)
            if self.__cnt < 6:
                self.__cnt += 1
                self.pw1.setXRange(center_freq - 0.1, center_freq + 0.1)
                self.pw2.setXRange(1, 60000)

            if self.p1_y_max < (power.max() + max_space/2) or (self.p1_y_max - power.max()) > max_space/2:
                self.p1_y_max = power.max() + max_space
                changed = True
            if self.p1_y_min > (power.min() + min_space/2) or (power.min() - self.p1_y_min) > min_space/2:
                self.p1_y_min = power.min() - min_space
                changed = True
            if changed:
                self.pw1.setYRange(self.p1_y_min, self.p1_y_max)
        else:
            self.la1.setText("{}, Pilot 19khz: {}dB".format(self.titletext, round(float(text))))
            self.p2.setData(freqs, power)
            if self.p2_y_max < (power.max() + max_space/2) or (self.p2_y_max - power.max()) > max_space/2:
                self.p2_y_max = power.max() + max_space
                changed = True
            if self.p2_y_min > (power.min() + min_space/2) or (power.min() - self.p2_y_min) > min_space/2:
                self.p2_y_min = power.min() - min_space
                changed = True
            if changed:
                self.pw2.setYRange(self.p2_y_min, self.p2_y_max)

    def closeEvent(self, event):
        # do stuff
        self.__close()

    def __close(self):
        self.__cnt = 0
        self.notice.emit(self)
        self.la1.setText('')
        self.p1.setData([0],[0])
        self.p2.setData([0],[0])
        self.hide()
        

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ex = ExMain()
    ex.show()
    sys.exit(app.exec_())