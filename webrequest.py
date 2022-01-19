from multiprocessing.dummy import Pool

import requests, json
import sqlmanger
import datetime
import time

class jyweb():
    def __init__(self, myid):
        self.id = myid
        self.pool = Pool(4)
        self.lastcalltime = 0

    def send(self, data:dict, pool=None):
        if pool is None:
            pool = Pool(4)
        #Center_freq,Center_dB,Correction_dB,PilotCompare_dB,Longitude,Latitude,DateTime
        
        data['key'] = self.id
        pool.apply_async(requests.post, args=['http://220.71.157.9:35261/jy.php'], kwds={'data': data, 'headers':{'Sexyjy':'ss'}},
                        callback=self.on_success, error_callback=self.on_error)
    
    def on_success(self, r):
        if r.status_code == 200:
            print('ur data is work! {}'.format(r.text))
            try:
                con = sqlmanger.sql()
                con.remove(int(r.text))
                con.close()
                con = None

            except Exception as ex:
                print(ex)
        else:
            print('code: {}'.format(r.status_code))
            pass
        
    def on_error(self, ex: Exception):
        print(f'Post requests failed: {ex}')
    
    def sendall(self, rows):
        if(time.time() - self.lastcalltime > 10):
            for row in rows:
                self.send(row, self.pool)
            self.lastcalltime = time.time()
