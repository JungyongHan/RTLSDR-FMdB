from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import time
import configparser
import math
import numpy as np
import pyrtlsdr
import gpsd
import csvsave
import configmanger
import qt_mainwindow, qt_sdrsetting, qt_programsetting, qt_freqsetting, qt_gpschecking ,qt_thread_worker

class Main(QMainWindow):
    def __init__(self):
        def freq_default(num, freq = 0):
            return {'num': num, 'freq':freq, 'show': False, 'IF': None, 'MPX': None, 'None': False}

        super().__init__()
        self.manger = configmanger.config('./config.ini')
        self.setWindowTitle("전계강도 측정용 프로그램")
        self.freqs = []
        for i in range(6):
            self.freqs.append(freq_default(i, self.manger.freqlist[i]))
        

        self.pause = False
        self.setFixedSize(800, 450)

        #-- module load
        self.rtlsdr = pyrtlsdr.Rtlsdr()
        self.gpsd = gpsd.gpsd(self.manger.COM)
        self.csvsave = csvsave.csvtool(self.manger.path, self.manger.distance)
        
        #-- ui load
        self.win_main = qt_mainwindow.Mainwindow()
        self.win_sdrset = qt_sdrsetting.Window(self.rtlsdr)
        self.win_proset = qt_programsetting.Window()
        self.win_frqset = qt_freqsetting.Window()
        self.win_gps = qt_gpschecking.Window()

        self.win_proset.csvtool = self.csvsave
        self.win_frqset.freqs = self.freqs
        self.win_frqset.freqtextchg()

        #-- ui button connect
        self.win_main.win_frqset.clicked.connect(self.win_open)
        self.win_main.win_sdrset.clicked.connect(self.win_open)
        self.win_main.win_proset.clicked.connect(self.win_open)
        self.win_main.win_gps.clicked.connect(self.win_open)
        self.win_main.testbtn.clicked.connect(self.testbnt_connect)

        #-- ui signal connect
        self.win_main.spectrum.connect(self.callback_spectrum)
        self.win_sdrset.subsignel.connect(self.callback_sdrdata)
        self.win_proset.subsignel.connect(self.callback_setting)
        self.win_frqset.subsignel.connect(self.callback_setting)

        #-- ui set
        self.setCentralWidget(self.win_main)
        self.show()
        
        #-- worker thread load
        self.threadpool = QThreadPool()
        worker = qt_thread_worker.Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)


        #-- config loader

    '''
        conf = configparser.ConfigParser()
        section_list = conf.sections()
        conf.has_section("section_name")
        opt_val_list = conf.items("section_name")
        train_path = conf.get("section_name", "option_name")


        self.netconnector = QThreadPool()
        worker = qt_thread_worker.Worker(self.net_connect) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        self.netconnector.start(worker)
         '''
    def progress_fn(self, n):
        #print("%d%% done" % n)
        pass

    def print_output(self, s):
        print(s)
        
    def thread_complete(self):
        print("THREAD COMPLETE!")

    def net_connect(self, progress_callback):
        while True:
            time.sleep(10)
            print("ㅋㅋㅋㄹㅇ")
   

    def execute_this_fn(self, progress_callback):
        def __f(val):
            return np.float(val)

        def simulalvalue(defination, range):
            sim = 9e6
            value = 0
            answer = 0
            for idx, x in np.ndenumerate(range):
                if abs(defination - x) < sim:
                    #print(x)
                    sim = abs(defination - x)
                    value = x
                    answer = idx
            return answer[0]

        np2float = np.vectorize(__f)        # numpy  -> float 변환 함수
        freqlow = freqcenter = freqhigh= 0  # 초기화
        pliotlow = pliotpeak = pliothigh = 0            # ''
        self.test_turnel = False
        while True:
            data_list = []                  # 저장될 주파수 데이터값 저장
            Maybe_in_tunnel = False         # 연결된 위성의 수가 줄어들 경우 저장용(터널)
            # GPS 데이터 값을 받아온 후, 연결된 위성 리스트를 가져옴
            gps_data = self.gpsd.getData()  
            Satellites_list = self.gpsd.getSatellites()
            # 위성표시를 위해 QtTABLE 항목 업데이트
            self.win_gps.table_update.emit(Satellites_list)
            # 소수점 이하 절삭
            try:
                gps_data['Longitude'] = round(gps_data['Longitude'], 5)
                gps_data['Latitude'] = round(gps_data['Latitude'], 5)
            except:
                pass
            try:
                satellite_cnt = len(list(filter(lambda x: x['USED'] and int(x['SNR']) > 15, Satellites_list['GP']['satellites'])))
                # 위성 수 4개 미만일 경우, GPS값을 믿을 수 없음
                # 좀 더 빡세게 하기 위해 5개 미만은 못믿는 gps데이터라 판정
                # pdop 관련 pipegps.py에서 처리
                if satellite_cnt < 5:
                    Maybe_in_tunnel = True
            except Exception as ex:
                satellite_cnt = 'n/a'
                '''
                from sys import stdin, stdout
                stdout.write('gps satellite error :{}'.format(ex))
                '''
            
            # GPS 데이터 값 GUI 표시
            if gps_data['Longitude'] != 0 and gps_data['Latitude'] != 0:
                if Maybe_in_tunnel:
                    color = "#6E6E6E"
                else:
                    color = "#ffffff"
                self.win_main.gpsupdate.emit('<html><head/><body><p><span style="font-size:18pt; font-weight:600; color:{};">위도:{} 경도:{} 위성:{}</span></p></body></html>'.format(color, gps_data['Longitude'], gps_data['Latitude'], satellite_cnt))
                #<html><head/><body><p><span style=" font-size:18pt; font-weight:600; color:#9f9f9f;">위도:xyz 경도:xyz</span></p></body></html>
            else:
                self.win_main.gpsupdate.emit("wait gps load")
                #print(gps_data)

            '''
            RTLSDR 측정된 데이터 IP 변환 후 MPX
            '''
            for freqdata in self.freqs:
                if self.pause:  # SDR 세팅 GUI가 열려있을 경우
                    break
                    
                if freqdata['freq'] != 0:
                    total_data = {}
                    __freq = float(freqdata['freq']) * int(1e6) # Mhz -> Hz
                    data = self.rtlsdr.run(__freq)
                    if data is None:
                        continue
                    #print("get time :", time.time() - start) 
                    IF_freqs = np2float(((data['IF'][0])/1e6 * self.rtlsdr.sample_rate/2) + int(__freq)/1e6)
                    IF_power = 10 * np.log10(data['IF'][1])
                    
                    if freqcenter == 0:
                        freqcenter = simulalvalue(__freq / 1e6, IF_freqs)
                        freqlow = simulalvalue((__freq - 20e3) / 1e6, IF_freqs)
                        freqhigh = simulalvalue((__freq + 20e3) / 1e6, IF_freqs)
                    
                    center, low, high = \
                        IF_power[freqcenter], \
                        IF_power[freqlow], \
                        IF_power[freqhigh]
                    
                    MPX_freqs = data['MPX'][0]
                    MPX_power = 10 * np.log10(data['MPX'][1])

                    if pliotlow == 0:
                        pliotlow = simulalvalue(17e3, MPX_freqs)
                        pliothigh = simulalvalue(18.6e3, MPX_freqs)
                        pliotpeak = simulalvalue(19e3, MPX_freqs) 
                        
                    total_data['Center_freq'] = str(freqdata['freq']) + 'Mhz'
                    total_data['Center_dB'] = math.floor(center)
                    total_data['Gain'] = getattr(self.rtlsdr, 'gain')

                    # 중심 주파수에서 +-20khz (2 고조파)의 피크값 + 중심 주파수 피크값의 평균값
                    total_data['Correction_dB'] = math.floor(
                        (((center + low) / 2) + ((center + high) / 2)) / 2) 
                    
                    # MPX 19khz 에서 17khz의 차이값
                    total_data['PilotCompare_dB'] = math.floor(
                        (MPX_power[pliotpeak]) - (np.mean(MPX_power[pliotlow:pliothigh])))
                    
                    # 스펙트럼 gui가 열렸을 경우, qtgraph 업데이트
                    if freqdata['show']:
                        self.win_main.win.sender.emit(1, IF_freqs, IF_power, total_data['Correction_dB'])
                        self.win_main.win.sender.emit(2, MPX_freqs, MPX_power, total_data['PilotCompare_dB'])#MPX_power[pliotpeak])

                    # 메인 화면 주파수 피크값 업데이트
                    self.win_main.reloading.emit(freqdata['num'], total_data)
                    data_list.append(total_data)
                    freqdata['None'] = False
                    #print("end time :", time.time() - start)
                else:
                    if not freqdata['None']:
                        self.win_main.reloading.emit(self.freqs.index(freqdata), None)
                        freqdata['None'] = True
            if len(data_list) > 0:  
                self.csvsave.save(gps_data, data_list, Maybe_in_tunnel) # 저장된 데이터 csv파일로 저장시도
            self.win_main.gps_distance_label.setText("{0}km    {1}km/h".format(math.floor((self.csvsave.record_distance + self.csvsave.temp_distance)/1e3), gps_data['Speed']))
            #print(self.csvsave.temp_distance)
            if self.csvsave.temp_distance <= self.csvsave.distance_for_calcu:
                varint = int((self.csvsave.temp_distance/self.csvsave.distance_for_calcu)*100)
                #print(varint)
                if varint <= 100:
                    self.win_main.barupdate.emit(varint)
            time.sleep(0.01)
 
    def testbnt_connect(self):
        if self.test_turnel:
            self.test_turnel = False
        else:
            self.test_turnel = True
            self.csvsave.record_lat -= 0.00002

    def win_open(self):
        sending_button = self.sender()
        try:
            win = getattr(self, sending_button.objectName())
            if win == self.win_sdrset:
                self.pause = True
            win.show()
        except Exception as ex:
            print(ex)


    def callback_setting(self, data):
        if data == 'distance':
            self.manger.distance = self.csvsave.distance_for_calcu
        elif data == 'freq':
            self.manger.set_freqs(self.freqs)
        
        self.manger.save()

    def callback_sdrdata(self, data):   
        #sdr 설정 변경
        for i in data:
            setter = getattr(self.rtlsdr, i['name'])
            if setter != i['value']:
                try:
                    setattr(self.rtlsdr, i['name'], i['value'])
                    try:
                        setattr(self.manger, i['name'], i['value'])
                        print(i['name'])
                        self.manger.save()
                    except:
                        pass
                    print('set {0}:{1}'.format(i['name'], i['value']))
                except:
                    print('too fast setting')
        self.pause = False

    def callback_spectrum(self, data, showbool):
        num = int(data)
        for freq in self.freqs:
            freq['show'] = False
        self.freqs[num]['show'] = showbool

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)

    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    myWindow = Main()
    myWindow.show()
    app.exec_()