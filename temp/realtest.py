
from multiprocessing.dummy import Pool
import requests, json

import csv
import math

def send(data:dict, pool=None):
    if pool is None:
        pool = Pool(4)
    #Center_freq,Center_dB,Correction_dB,PilotCompare_dB,Longitude,Latitude,DateTime
    pool.apply_async(requests.post, args=['http://220.71.157.9:35261/jy.php'], kwds={'data': data, 'headers':{'Sexyjy':'ss'}},
                    callback=on_success, error_callback=on_error)

def on_success(r):
    if r.status_code == 200:
        print('ur data is work! {}'.format(r.text))
    else:
        print('code: {}'.format(r.status_code))
        pass
        
def on_error(r):
    pass

def csvget(path, datalist):
    f = open(path, 'r', encoding='utf-8')
    rdr = csv.reader(f)
    for line in rdr:
        datalist.append(line)
    f.close()

path = "C:\\atemp\\tt.csv"
jylist = []
pool = Pool(4)
csvget(path, jylist)

for idx, jydata in enumerate(jylist):
    tempdic = {}
    tempdic['id'] = 123
    tempdic['Center_freq'] = jydata[3] + '1'
    tempdic['Center_dB'] = -1
    tempdic['Correction_dB'] = -1
    tempdic['PilotCompare_dB'] = jydata[7]
    tempdic['Longitude'] = jydata[0]
    tempdic['Latitude'] = jydata[1]
    tempdic['DateTime'] = '2020-11-17 09:21:00'
    tempdic['Tunnel'] = 2
    tempdic['Gain'] = "14.4"
    tempdic['key'] = "광주"
    
    send(tempdic, pool)

import time
time.sleep(30)