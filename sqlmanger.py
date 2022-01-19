import sqlite3
import os.path
import datetime
class sql:
    def __init__(self, dbpath):
        self.datadb = dbpath
        self.maxrow = 0
        filexitst = os.path.isfile(self.datadb)
        self.con = sqlite3.connect(self.datadb)
        self.con.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
        self.cursor = self.con.cursor()
        if not filexitst:
            #Center_freq,Center_dB,Correction_dB,PilotCompare_dB,Longitude,Latitude,DateTime
            self.cursor.execute("CREATE TABLE data(id INTEGER PRIMARY KEY, Center_freq text, Center_dB int, Correction_dB int, PilotCompare_dB int, Longitude real, Latitude real, DateTime timestamp, Gain real, Tunnel int)")
        self.con.commit()
        

    def __get_index(self):
        onrow = self.cursor.execute("SELECT id FROM data ORDER BY id DESC LIMIT 1").fetchone()
        if onrow is None:
            self.maxrow += 1
            return self.maxrow
        if onrow['id'] != self.maxrow:
            rows = self.cursor.execute("SELECT id FROM data").fetchall()
            index = 0
            for row in rows:
                if row['id'] - 1 == index:
                    index = row['id']
            self.maxrow = index + 1
        else:
            self.maxrow += 1
        return self.maxrow
    
    def close(self):
        self.con.close()

    def lastrow(self):
        onrow = self.cursor.execute("SELECT id FROM data ORDER BY id DESC LIMIT 1").fetchone()
        if onrow is None:
            return 0
        return int(onrow['id'])

    def input(self, data:dict):
        data['id'] = self.__get_index()
        self.cursor.execute('INSERT INTO data(id, Center_freq, Center_dB, Correction_dB, PilotCompare_dB, Longitude, Latitude, DateTime, Gain, Tunnel) VALUES (:id, :Center_freq, :Center_dB, :Correction_dB, :PilotCompare_dB, :Longitude, :Latitude, :DateTime, :Gain, :Tunnel);', data)
        self.con.commit()
    
    def remove(self, idx:int):
        self.cursor.execute('DELETE FROM data WHERE id={}'.format(idx))
        self.con.commit()

    def read(self):
        return self.cursor.execute("SELECT * FROM data LIMIT 31").fetchall()

'''
fakedic = {'Center_freq':'97.3Mhz','Center_dB':64.123456,'Correction_dB':64.123456,'PilotCompare_dB':64.123456,'Longitude':64.123456,'Latitude':64.123456,'DateTime':datetime.datetime.now(), 'Gain':13.4, 'Tunnel':0}

a = sql()

for i in range(1,1000):
    a.input(fakedic)
for row in a.read():
    print(row['id'])
    a.remove(row['id'])

print(a.read())
a.remove(1)
print(a.read())
'''