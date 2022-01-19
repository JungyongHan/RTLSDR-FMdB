from time import sleep
import datetime
import threading
import math
import pipegps

class gpsd:
    def __init__(self, gpsport):
        self.gps_thread = pipegps.DataStream(gpsport)  # Instantiate AGPS3 Mechanisms
        self.gps_thread.start()

    def getData(self):
        #self.gps_thread.run_thread()        # Throttle time to sleep after an empty lookup, default '()' 0.2 two tenths of a second
        timeset = 0
        return {'DateTime':   self.gps_thread.RMC['UTC'],
                'Speed':      self.gps_thread.RMC['Speed'],
                'Tunnel':     0,
                'Latitude':   self.__float_or_na(self.gps_thread.RMC['Latitude']),
                'Longitude':  self.__float_or_na(self.gps_thread.RMC['Longitude'])}

    def getSatellites(self):
        return self.gps_thread.GSV

    def __float_or_na(self, value):
        #https://stackoverflow.com/questions/24249609/converting-string-to-float-python-n-a
        try:
            return float(value) if value != 'N/A' else None
        except:
            return 0

if __name__ == "__main__":
    a = gpsd()
    for i in range(100):
        print(a.getsatellites())
        sleep(0.1)