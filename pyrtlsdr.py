import rtldoc

class Rtlsdr:
    def __init__(self):
        self.__rtlsdr = rtldoc.RTLSDR()
    
    def run(self, freq):
        return self.__rtlsdr.analyze(int(freq))

    @property
    def F_offset(self):
        return self.__rtlsdr.F_offset

    @property
    def BandWidth(self):
        return self.__rtlsdr.BandWidth
    
    @property
    def sample_rate(self):
        return self.__rtlsdr.sdr.sample_rate

    @property
    def gain(self):
        return self.__rtlsdr.sdr.gain

    @F_offset.setter
    def F_offset(self, value):
        self.__rtlsdr.F_offset = value

    @BandWidth.setter
    def BandWidth(self, value):
        self.__rtlsdr.BandWidth = value

    @sample_rate.setter
    def sample_rate(self, value):
        self.__rtlsdr.sdr.sample_rate = value

    @gain.setter
    def gain(self, value):
        self.__rtlsdr.sdr.gain = float(value)