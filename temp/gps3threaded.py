  
#!/usr/bin/env python3.5
# coding=utf-8
"""Threaded gps3 client"""
from __future__ import print_function

from threading import Thread
from time import sleep

try:  # This kludge to get around imports with files and directories the same name.
    import gps3.gps3 as gps3 # Python 3
except ImportError:
    from . import gps3  # Python 2

__author__ = 'Moe'
__copyright__ = 'Copyright 2016  Moe'
__license__ = 'MIT'
__version__ = '0.2.3'

HOST = '127.0.0.1'  # gpsd
GPSD_PORT = 2947  # defaults
PROTOCOL = 'json'  # "


class GPS3mechanism(object):
    """Create threaded data stream as updated object attributes
    """

    def __init__(self):
        self.socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()

    def stream_data(self, host=HOST, port=GPSD_PORT, enable=True, gpsd_protocol=PROTOCOL, devicepath=None):
        """ Connect and command, point and shoot, flail and bail
        """
        self.socket.connect(host, port)
        self.socket.watch(enable, gpsd_protocol, devicepath)

    def unpack_data(self, usnap=.2):  # 2/10th second sleep between empty requests
        """ Iterates over socket response and unpacks values of object attributes.
        Sleeping here has the greatest response to cpu cycles short of blocking sockets
        """
        for new_data in self.socket:
            if new_data:
                self.data_stream.unpack(new_data)
            else:
                sleep(usnap)  # Sleep in seconds after an empty look up.

    def run_thread(self, usnap=.2, daemon=True):
        """run thread with data
        """
        # self.stream_data() # Unless other changes are made this would limit to localhost only.
        try:
            gps3_data_thread = Thread(target=self.unpack_data, args={usnap: usnap}, daemon=daemon)
        except TypeError:
            # threading.Thread() only accepts daemon argument in Python 3.3
            gps3_data_thread = Thread(target=self.unpack_data, args={usnap: usnap})
            gps3_data_thread.setDaemon(daemon)
        gps3_data_thread.start()

    def stop(self):
        """ Stop as much as possible, as gracefully as possible, if possible.
        """
        self.stream_data(enable=False)  # Stop data stream, thread is on its own so far.
        print('Process stopped by user')
        print('Good bye.')  # You haven't gone anywhere, re-start it all with 'self.stream_data()'


if __name__ == '__main__':
    from gps3.misc import add_args
    args = add_args()

    gps3_thread = GPS3mechanism()  # The thread triumvirate
    gps3_thread.stream_data(host=args.host, port=args.port, gpsd_protocol=args.gpsd_protocol)
    gps3_thread.run_thread(usnap=.2)  # Throttle sleep between empty lookups in seconds defaults = 0.2 of a second.

    seconds_nap = int(args.seconds_nap)  # Threaded Demo loop 'seconds_nap' is not the same as 'usnap'
    while True:
        sleep(0.2)
        print(gps3_thread.data_stream.__dict__)
        print('\nGPS3 Thread still functioning at {}'.format(gps3_thread.data_stream.TPV['time']))
        print('Lat:{}  Lon:{}  Speed:{}  Course:{}'.format(gps3_thread.data_stream.TPV['lat'],
                                                             gps3_thread.data_stream.TPV['lon'],
                                                             gps3_thread.data_stream.TPV['speed'],
                                                             gps3_thread.data_stream.TPV['track']))
        if isinstance(gps3_thread.data_stream.SKY['satellites'], list):  # Nested lists of dictionaries are strings before data is present
            for sats in gps3_thread.data_stream.SKY['satellites'][0:10]:
                print('{PRN:>2}   {el:>6}   {az:>5}   {ss:>5}   {used:}'.format(**sats))
#
######
# END