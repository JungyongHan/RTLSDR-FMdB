from threading import Thread
from time import sleep
from datetime import datetime, timedelta
try:
    import serial
except:
    pass
from functools import reduce

class DataStream(object):
    packages = {
    'GGA' : ['UTC','Latitude','NS','Longitude','EW','Fix','Used_Sat','HDOP','Altitude','Altitude Units'], #GeoidSep, SepUnit, DGPSAge,DGPSStID, checksum]
    'RMC' : ['UTC','Status','Latitude','NS','Longitude','EW','Speed','Direction','UTCDATE'], #MagneticVariation,checksum]
    'GSV' : ['temp'] #['Mode']['satellites']['ID','Elevation','Azimuth','SNR']
    }

    def __init__(self, gpsport):
        try:
            self.notwork = False
            #self.ser = serial.Serial('/dev/ttyACM0', 9600)
            self.ser = serial.Serial(gpsport, 9600)
        except Exception as ex:
            print(f"unport {ex}")
            self.notwork = True

        for package_name, dataset in self.packages.items():
            _emptydict = {key: 'n/a' for key in dataset}
            setattr(self, package_name, _emptydict)
        
    def isData_Valid(self, data_dic, checksum):
        def ord_or_value(value):
            try:
                return ord(value)
            except:
                return value
        data_dic[0] = data_dic[0].replace('$','')
        line = ','.join(data_dic)
        try:
            hexa = hex(reduce(lambda x,y: ord_or_value(x) ^ ord_or_value(y), line)).replace('0x','').upper()
            
            if hexa != checksum.strip():
                return False
            return True
        except:
            return False

    def chksum_nmea(self, sentence):
        import re
        # This is a string, will need to convert it to hex for 
        # proper comparsion below
        cksum = sentence[len(sentence) - 2:]
        
        # String slicing: Grabs all the characters 
        # between '$' and '*' and nukes any lingering
        # newline or CRLF
        chksumdata = re.sub("(\n|\r\n)","", sentence[sentence.find("$")+1:sentence.find("*")])
        
        # Initializing our first XOR value
        csum = 0 
        
        # For each char in chksumdata, XOR against the previous 
        # XOR'd char.  The final XOR of the last char will be our 
        # checksum to verify against the checksum we sliced off 
        # the NMEA sentence
        
        for c in chksumdata:
           # XOR'ing value of csum against the next char in line
           # and storing the new XOR value in csum
           csum ^= ord(c)
        
        # Do we have a validated sentence?
        if hex(csum) == hex(int(cksum, 16)):
           return True

        return False


    def start(self):
        if self.notwork:
            return
        try:
            daemon_thread = Thread(target=self.__unpack, daemon=True)
        except TypeError:
            daemon_thread = Thread(target=self.__unpack)
            daemon_thread.setDaemon(True)
        daemon_thread.start()

    def __unpack(self):
        def rewrite_data(data, rmcUTCdate):
            for key in data:
                if data[key] == '':
                    continue
                try:
                    if 'UTC' == key:
                        if data[key] == 'n/a' or rmcUTCdate == 'n/a':
                            continue
                        data[key] = datetime.strptime(rmcUTCdate + data[key],"%d%m%y%H%M%S.00")
                    
                    if 'Latitude' == key or 'Longitude' == key:
                        mPos = data[key].find(".")-2
                        if mPos < 1:
                            continue
                        degree = float(data[key][:mPos])
                        minute = float(data[key][mPos:])
                        converted_degree = float(degree) + float(minute) / float(60) 
                        if data['EW'] == "W":
                            converted_degree = -converted_degree
                        elif data['NS'] == "S":
                            converted_degree = -converted_degree
                        data[key] = float(round(converted_degree, 8))
                    
                    if 'Speed' == key:
                        data[key] = round(float(data[key]) * 1.852)

                except Exception as ex:
                    pass
                    #from sys import stdin, stdout
                    #stdout.write('cant rewrite date of {}:{}, {}'.format(key, data[key], ex))
        '''
        f = open("Z:\\emptygpsdata.txt", 'r')
        lines = f.readlines()
        f.close()
        cnt = -1
        '''
        rmc = getattr(self, 'RMC')
        gga = getattr(self, 'GGA')
        gsv = {}
        satellites_list = []

        while True:
            try:
                data = self.ser.readline().decode().replace('\n','').replace('\r','')
            
            except:
                pass
            '''
            cnt += 1
            if cnt == len(lines):
                break
            data = lines[cnt]
            '''
            #print(len(data), data)
            if len(data) > 1:
                #print(len(data))
                #print(data)
                gps_parse = data.split(',')

                checksplit = gps_parse[len(gps_parse) - 1].split('*')
                gps_parse[len(gps_parse) - 1] = checksplit[0]
                
                try:
                    if not self.chksum_nmea(data):
                        #print(data)
                        continue
                except Exception as ex:
                    #print(ex)
                    continue
                
                
                callid = 'RMC'
                if callid in gps_parse[0]: # GNSS DATA
                    satellites_list = []
                    rmc = getattr(self, callid).copy()
                    try:
                        for i in range(len(self.packages[callid])):
                            rmc[self.packages[callid][i]] = gps_parse[i + 1]
                    except:
                        pass
                    
                    rewrite_data(rmc, rmc['UTCDATE'])
                    rewrite_data(gga, rmc['UTCDATE'])
                    setattr(self, 'RMC', rmc)
                    setattr(self, 'GGA', gga)
                    setattr(self, 'GSV', gsv)
                    gsv = {}
                    '''
                    print("\n")
                    print(getattr(self, 'RMC'))
                    print(getattr(self, 'GGA'))
                    print(getattr(self, 'GSV'))
                    '''
                
                callid = 'GGA'
                if callid in gps_parse[0]: # GPS 수신 데이터
                    gga = getattr(self, callid).copy()
                    for i in range(len(self.packages[callid])):
                        gga[self.packages[callid][i]] = gps_parse[i + 1]
                    #print(gga)
               

                callid = 'GSA'
                if callid in gps_parse[0]: # GPS 연결된 위성 ID 리스트
                    #print('called')
                    satellites_buff_list = [gps_parse[i] for i in range(3, 14) if gps_parse[i] != '']
                    try:
                        satellites_list += satellites_buff_list
                        pdop = float(gps_parse[15])
                    except:
                        pdop = 10

                callid = 'GSV'
                if callid in gps_parse[0]: # 탐지된 GLONASS 위성 정보
                    
                    mode = gps_parse[0].replace('$','').replace(callid,'')
                    #print(mode)
                    if mode in gsv:
                        if gps_parse[2] == str(1) or type(gsv[mode]) == str:
                            gsv[mode] = {}
                            gsv[mode]['satellites'] = []
                            gsv[mode]['totalcnt'] = 'n/a'
                    else:
                        gsv[mode] = {}
                        gsv[mode]['satellites'] = []
                        gsv[mode]['totalcnt'] = 'n/a'
                    gsv[mode]['totalcnt'] = gps_parse[3]
                    tt = ['ID','Elevation','Azimuth','SNR']

                    for i in range(1, 5):
                        temp = {}
                        staNum = i * 4
                        if staNum >= len(gps_parse):
                            break
                        for k in range(staNum, staNum + 4):
                            temp[tt[k % staNum]] = gps_parse[k]
                        temp['USED'] = (temp['ID'] in satellites_list) and pdop < 6
                        
                        gsv[mode]['satellites'].append(temp)
                    if gps_parse[1] == gps_parse[2]:
                        #print(satellites_list)
                        #print(getattr(self, callid),"\n")
                        pass


if __name__ == "__main__":
    x = DataStream()
    x.start()
    while True:
        sleep(0.1)
        pass


'''

def dms_to_dec(value, dir): 
    mPos = value.find(".")-2 
    degree = float(value[:mPos]) 
    minute = float(value[mPos:]) 
    converted_degree = float(degree) + float(minute)/float(60) 
    if dir == "W": 
        converted_degree = -converted_degree 
    elif dir == "S": 
        converted_degree = -converted_degree 
        return "%.9f" % float(round(converted_degree, 8)) 

def format_time(value):
    pre = strftime("%Y-%m-%dT") 
    hour = value[:2] 
    minute = value[2:4] 
    second = value[4:6] 
    timeval = pre + hour + ":" + minute + ":" + second + "Z" 
    return timeval 

def convert(inputName, outputName): 
    data = open(inputName, "r") 
    file = open(outputName, 'w') 
    file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<gpx version=\"1.0\">\n") 
    file.write("<trk>\n<trkseg>\n") 
    for line in data: 
        gpgga = line.split(',') 
        if gpgga[0] == '$GPGGA': 
            lat_val = dms_to_dec(gpgga[2], gpgga[3]) 
            long_val = to_dec(gpgga[4], gpgga[5]) 
            strtrkpt = "<trkpt lat=\"" + str(lat_val) + "\" lon=\"" + str(long_val) + "\"> <time>" + format_time(gpgga[1]) + "</time> </trkpt>\n" 
            file.write(strtrkpt) 
            file.write("</trkseg>\n</trk>\n</gpx>\n") 
            file.close() 
        
###################################################### # 
#main 
convert('nmea.txt', 'nmea.gpx')
print "Done!"
'''
