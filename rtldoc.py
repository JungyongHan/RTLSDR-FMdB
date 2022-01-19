#-*- coding:utf-8 -*-
from rtlsdr import RtlSdr
import gc
import numpy as np
import scipy.signal as signal
import multiprocessing as mp
import threading
import time
import matplotlib
matplotlib.use('Agg') 
from matplotlib import mlab
'''
class Thread_Read(threading.Thread):
    def __init__(self, RTLSDR, samples):
      threading.Thread.__init__(self)
      self.sdr = RTLSDR
      self.samples = samples
      self.stopit = False

    def run(self):
        print ("Starting read")
        while not self.stopit:
            # RTL SDR samples 읽기
            # 지정된 read_time 만큼 시간이 걸림
            self.samples.put(self.sdr.sdr.read_samples(self.sdr.N))
'''
class RTLSDR(object):
    def __init__(self):
        self.sdr = RtlSdr()
        self.F_offset = 250000              # DC SPIKE 대비 회피 주파수
        self.BandWidth = int(0.2e6)
        self.sdr.sample_rate = int(1.024e6)   # Hz
        self.sdr.gain = 14.4                  # Supported gain values (29): 0.0 0.9 1.4 2.7 3.7 7.7 8.7 12.5 14.4 15.7 16.6 19.7 20.7 22.9 25.4 28.0 29.7 32.8 33.8 36.4 37.2 38.6 40.2 42.1 43.4 43.9 44.5 48.0 49.6 

    def __getdata(self, sampleNum = 1024*64):
        return self.sdr.read_samples(sampleNum)

    def analyze(self, freq):
        try:
            Fc = freq - self.F_offset           # 측정할주파수에서 회피된 주파수
            self.sdr.center_freq = Fc           # Hz

            samples = self.__getdata()
        except:
            print('RTL DATA IS SOMETHING STRANGE !!!\n')
            return None
        x1 = np.array(samples).astype("complex64")
        # 현재 주파수 값을 -> 방향으로 F_offset 만큼 이동하기 위한 동기주파수 생성
        # e ^(푸리에급수 * 회피주파수 / (샘플레이트 * x1의 데이터크기)) 
        fc1 = np.exp(-1.0j * 2.0 * np.pi * self.F_offset / self.sdr.sample_rate * np.arange(len(x1)))
        # 원래 데이터에서 회피주파수부분을 이동(제외)시킴
        x2 = x1 * fc1
        #freqs, power = signal.welch(x2, nfft=2048, fs=self.sdr.Fs) #넘느림 이거
        power, freqs = mlab.psd(x2, NFFT=2048, Fs=self.sdr.sample_rate / 1e6)
        spectrum_IF = [freqs, power]
        
        # FM 라디오 디지털 필터
        # MPX
        dec_rate = int(self.sdr.sample_rate / self.BandWidth)
        x3 = signal.decimate(x2 , dec_rate)
        # 다운샘플링된 데이터의 샘플레이트 계산
        y4 = x3[1:] * np.conj(x3[:-1])
        x4 = np.angle(y4)
        self.Fs_y = self.sdr.sample_rate/dec_rate
        power, freqs = mlab.psd(x4, NFFT=2048, Fs=self.Fs_y)
        spectrum_MPX = [freqs, power]
        returnvalue = {'IF' : spectrum_IF, 'MPX' : spectrum_MPX, 'samples' : x4}
        return returnvalue

    def deemphasis_filter(self, data):
        # samples 에 신호를 주어 Fs_y만큼의 샘플레이트를 갖게해줌
        d = self.Fs_y * 75e-6   # 시정수 추가
        x = np.exp(-1/d)        # Calculate the decay between each sample
        b = [1-x]               # Create the filter coefficients
        a = [1,-x]
        x5 = signal.lfilter(b, a, data['samples'])

        # 높은 주파수 데이터 삭제 후 44-48 kHz 사이로 다운샘플링
        audio_freq = 44100.0
        dec_audio = int(self.Fs_y/audio_freq)
        Fs_audio = self.Fs_y / dec_audio

        x6 = signal.decimate(x5, dec_audio)
        x6 *= 10000 / np.max(np.abs(x6))
        #print(Fs_audio)
        return {'sounds' : x6, 'samplerate' : Fs_audio}


