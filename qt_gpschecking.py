import sys, os
from PyQt5.QtWidgets import * 
from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from sys import stdin, stdout
import qt_dialog
ui_path = os.path.dirname(os.path.abspath(__file__))
form_class = uic.loadUiType(os.path.join(ui_path, "ui/gpschecking.ui"))[0]

class Window(QWidget, form_class):
    table_update = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("GPS 위성상태")
        self.btn_callback.clicked.connect(self.btn_clicked)
        self.table_update.connect(self.update)

    def btn_clicked(self):
        '''
        tt = {'GP': {'satellites': [{'ID': '02', 'Elevation': '67', 'Azimuth': '347', 'SNR': '31', 'USED': True}, {'ID': '04', 'Elevation': '03', 'Azimuth': '035', 'SNR': '', 'USED': False}, {'ID': '05', 'Elevation': '52', 'Azimuth': '271', 'SNR': '33', 'USED': True}, {'ID': '06', 'Elevation': '58', 'Azimuth': '075', 'SNR': '35', 'USED': True}, {'ID': '07', 'Elevation': '09', 'Azimuth': '100', 'SNR': '', 'USED': False}, {'ID': '09', 'Elevation': '32', 'Azimuth': '051', 'SNR': '15', 'USED': True}, {'ID': '12', 'Elevation': '16', 'Azimuth': '259', 'SNR': '21', 'USED': True}, {'ID': '13', 'Elevation': '14', 'Azimuth': '191', 'SNR': '', 'USED': False}, {'ID': '17', 'Elevation': '15', 'Azimuth': '157', 'SNR': '23', 'USED': True}, {'ID': '19', 'Elevation': '34', 'Azimuth': '162', 'SNR': '17', 'USED': True}, {'ID': '25', 'Elevation': '10', 'Azimuth': '288', 'SNR': '10', 'USED': False}, {'ID': '29', 'Elevation': '07', 'Azimuth': '323', 'SNR': '', 'USED': False}, {'ID': '30', 'Elevation': '05', 'Azimuth': '131', 'SNR': '', 'USED': False}, {'ID': '50', 'Elevation': '49', 'Azimuth': '180', 'SNR': '29', 'USED': True}], 'totalcnt': '14'}, 'GL': {'satellites': [{'ID': '65', 'Elevation': '33', 'Azimuth': '224', 'SNR': '', 'USED': False}, {'ID': '71', 'Elevation': '44', 'Azimuth': '029', 'SNR': '', 'USED': False}, {'ID': '72', 'Elevation': '78', 'Azimuth': '257', 'SNR': '', 'USED': False}, {'ID': '85', 'Elevation': '09', 'Azimuth': '137', 'SNR': '', 'USED': False}, {'ID': '86', 'Elevation': '61', 'Azimuth': '116', 'SNR': '', 'USED': False}, {'ID': '87', 'Elevation': '46', 'Azimuth': '336', 'SNR': '22', 'USED': True}, {'ID': '88', 'Elevation': '09', 'Azimuth': '324', 'SNR': '', 'USED': False}], 'totalcnt': '07'}}
        self.update(tt)
        '''
        #self.subsignel.emit('12')
        self.hide()

    def update(self, sattlies):
        self.tableWidget.clearContents()
        try:
            for idx, data in enumerate(sattlies['GP']['satellites']):
                for idxx, datax in enumerate(data):
                    self.tableWidget.setItem(idx, idxx, QTableWidgetItem(str(data[datax])))
        except KeyError:
            #stdout.write('not update gps table')
            pass
        self.tableWidget.sortItems(4, Qt.DescendingOrder)
        #print('next')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    app.exec_()