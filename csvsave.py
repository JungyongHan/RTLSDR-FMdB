import csv
import math
import glob
import datetime
import time
import os

import sqlmanger
import webrequest

from pathlib import Path
from PyQt5.QtCore import pyqtSignal
class csvtool:
    def __init__(self, logpath, distance):
        self.csv_list = []
        self.record_lon = 0
        self.record_lat = 0
        self.record_distance = 0
        self.__lastrow = -1
        self.__record_list = []
        self.split_files = True
        self.field_name_list = ['Center_freq', 'Center_dB' ,'Correction_dB', 'PilotCompare_dB', 'Longitude', 'Latitude', 'Gain' ,'DateTime', 'Tunnel']
        self.log_path = logpath
        #self.log_path = "/home/pi/log/*"
        self.temp_distance = 0
        self.distance_for_calcu = distance
        self.saved_time = 0
        self.web = webrequest.jyweb('광주')

        
        self.webrqeust = True

    def save(self, gps_data, values, tunnel = False):
        saved = False
        if tunnel:
            if(self.record_lon != 0 and self.record_lat != 0):
                
                for data in values:
                    data['DateTime'] = gps_data['DateTime']
                self.__record_list.append(values)
        else:     
            if(gps_data['Longitude'] != 0 and gps_data['Latitude'] != 0): # tunnel save
                self.temp_distance = self.__calcu(gps_data)
                if(len(self.__record_list) > 2 and self.temp_distance > 33):
                    print('in tunnel length {0}'.format(self.temp_distance))
                    if(self.record_lon != 0 and self.record_lat != 0):
                        value_cal = self.__distance_split(gps_data['Longitude'], gps_data['Latitude'])
                        for point_data in value_cal:
                            for data in point_data:
                                self.__writer(data)
                        self.__record_list.clear()
                #초기 gps 값 세팅
                if(self.record_lon == self.record_lat == 0):
                    self.record_lon, self.record_lat = gps_data['Longitude'], gps_data['Latitude']
                    self.temp_distance = 0
                else:
                    #시속 200(초속 55.5)이상 속도로 달리면 gps값 에러로 보고 데이터값 재 정의
                    if(self.temp_distance > 55.5 * (time.time() - self.saved_time)):
                        self.record_lon, self.record_lat = gps_data['Longitude'], gps_data['Latitude']
                        print('too high speed : {0}'.format(gps_data['Speed']))
                    else:
                        #지정된 거리(기본값 150m) 이상 진행할 경우, 해당위치 기록
                        if(self.temp_distance > self.distance_for_calcu):
                            self.__record_list.clear()
                            for data in values:
                                self.__writer({**gps_data, **data})
                            saved = True

        if saved:
            print('save')
            self.record_lon, self.record_lat = gps_data['Longitude'], gps_data['Latitude']
            self.record_distance = math.floor(self.record_distance + self.temp_distance)
            self.temp_distance = 0
            self.saved_time = time.time()
            
        sqlite = sqlmanger.sql(self.log_path)
        if(sqlite.lastrow() > 30):
            '''
            try:
            '''
            data = sqlite.read()
            sqlite.close()
            self.web.sendall(data)
            sqlite = None
            '''
            except Exception as ex:
                print(ex)
                pass
            '''
    
    def __distance_split(self, lon, lat): #추측항법(dead reckoning)
        def split_evenly(total_list, split_cnt):
            center = len(total_list)//2
            a1 = (center)//((split_cnt-1)/2)
            a2 = (len(total_list)-center)//((split_cnt-1)/2)
            cnt = int((split_cnt-1)/2)
            aa1 = [int(i * a1) for i in range(cnt)]
            aa2 = [len(total_list) - 1 - int(i * a2) for i in range(cnt)]
            ex = aa1 + aa2
            ex.append(center)
            print(sorted(ex))
            return sorted(ex)
        #print(lat,lon)
        #print(self.record_lat, self.record_lon)
        distance_lat = abs(self.__calcu({'Latitude' : lat, 'Longitude' : self.record_lon}))
        distance_lon = abs(self.__calcu({'Latitude' : self.record_lat, 'Longitude' : lon}))
        reserved = distance_lat > distance_lon
        #print(distance_lat, distance_lon)
        if(reserved):
            x1, x2 = self.record_lat, lat
            y1, y2 = self.record_lon, lon
            split_x = distance_lat // self.distance_for_calcu + 1
        else:
            x1, x2 = self.record_lon, lon
            y1, y2 = self.record_lat, lat
            split_x = distance_lon // self.distance_for_calcu + 1
        #print((y1 - y2),(x1 - x2))
        m = (y1 - y2)/(x1 - x2) # 기울기
        n = y1 - (m * x1)       # 절편
        print('y={0}x+{1}[{2}]'.format(m, n, reserved))
        print('start {0} to end {1}'.format(x1, x2))
        split_cnt = 1
        for i in range(2, int(split_x) + 2):
            if(i * 2 + 1 > split_x or i * 2 + 1 > len(self.__record_list)):
                split_cnt = (i - 1) * 2 + 1
                break
        # self.__record_list -> temp_record_list -> data_list -> data

        split_list = split_evenly(self.__record_list, split_cnt)
        calcu_data = [self.__record_list[i] for i in split_list]
        
        for i in range(len(calcu_data)):
            x = x1 - ((x1 - x2) * (split_list[i] / len(self.__record_list)))
            y = m * x + n
            for data in calcu_data[i]:
                x = round(x, 5)
                y = round(y, 5)
                if not reserved:
                    data['Latitude'] = y
                    data['Longitude'] = x
                else:
                    data['Latitude'] = x
                    data['Longitude'] = y
                data['Speed'] = 0
                data['Tunnel'] = 1
        #print(calcu_data)
        return calcu_data
                     
    def __writer(self, data):
        if self.webrqeust:
            sqlite = sqlmanger.sql(self.log_path)
            sqlite.input(data)
            sqlite.close()
        else:
            with open(self.__getcurrent_file(data['Center_freq'].replace('.', '')), 'a', encoding='utf-8', newline='') as writer_csv:
                writer = csv.DictWriter(writer_csv, fieldnames=self.field_name_list)
                #print(data['Speed'])
                try:
                    del data['Speed']   #속도 항목 삭제
                    writer.writerow(data)
                    self.__lastrow = self.__lastrow + 1
                except:
                    print('DATA IS WRONG')

    def __calcu(self, current_gpsd):
        #https://janakiev.com/blog/gps-points-distance-python/
        R = 6372800  # Earth radius in meters
        lat1, lon1 = float(self.record_lat), float(self.record_lon)
        lat2, lon2 = current_gpsd['Latitude'], current_gpsd['Longitude']
        
        phi1, phi2 = math.radians(lat1), math.radians(lat2) 
        dphi       = math.radians(lat2 - lat1)
        dlambda    = math.radians(lon2 - lon1)
        
        a = math.sin(dphi/2)**2 + \
            math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        
        return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def __createFolder(self, path):
        sep = os.path.sep
        localpath = path.replace(sep + '*','')
        os.makedirs(localpath)
        print(localpath)

    def __getcurrent_file(self, freqname):
        path = self.log_path
        if self.split_files:
            path = path.replace("*", freqname + os.path.sep + "*")
        if not os.path.isdir(path.replace('*','')):
            self.__createFolder(path)
        title = ''
        file_list = glob.glob(path)
        file_list_csv = [file for file in file_list if file.endswith(".csv")]
        for file_csv in file_list_csv:
            filename = Path(file_csv).stem
            if(filename.count('-proc') != 0):
                if((self.__int_or_na(filename.replace('-proc','')) - int(self.__get_now_datetime().replace('-proc.csv', ''))) == 0):
                    if(self.__lastrow == -1):
                        self.__lastrow = self.__getrowcnt(file_csv)

                    if( self.__lastrow > 300):
                        while True:
                            temp_filename = filename.replace('-proc','') + '-' + str(time.strftime('%H%M%S', time.localtime(time.time()))) + '.csv'
                            print(temp_filename)
                            if(os.path.isfile(temp_filename) == False):
                                temp_dir = os.path.dirname(file_csv)
                                os.rename(file_csv, temp_dir + os.path.sep + temp_filename)
                                self.__lastrow = 0
                                break
                    else:
                        title = file_csv
                        break
        if(title == ''):
            title = path.replace('*','') + self.__get_now_datetime()
            with open(title, 'w', encoding='utf-8', newline='') as writer_csv:
                writer = csv.DictWriter(writer_csv, fieldnames=self.field_name_list)
                writer.writeheader()
        return title

    def __getrowcnt(self, filename):
        with open(filename) as f:
            return sum(1 for line in f)
    
    def __get_now_datetime(self):
        return datetime.datetime.now().strftime('%Y%m%d-proc.csv')

    def __int_or_na(self, value):
        try:
            return int(value) if value != 'N/A' else None
        except:
            return 0

if __name__ == "__main__":
    a = csvtool('c:\\tes\\*')
    #126.836 35.2129
    gps_data = {'Speed':1 , 'Latitude':126.842, 'Longitude':35.2159,}
    data =  [{'Center_freq':'97.30', 'Center_dB':'0','Correction_dB':'0', 'PilotCompare_dB':'0', 'DateTime':'00'}]
    a.save(gps_data, data)
    for x in range(100):
        gps_data = {'Speed':0, 'Latitude':126.842-x*0.0001, 'Longitude':35.2159+x*0.001, }
        data =  [{'Center_freq':'97.31', 'Center_dB':x,'Correction_dB':x, 'PilotCompare_dB':'0','DateTime':x}]
        a.save(gps_data, data, True)
    #gps_data = {'Speed':0, 'Latitude':126.8421, 'Longitude':35.21591, }
    a.save(gps_data, data, False)
