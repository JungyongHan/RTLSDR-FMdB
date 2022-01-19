import configparser

class config:
    def __init__(self, configpath):
        self.configpath = configpath
        self.read()
    
    def read(self):
        with open(self.configpath) as fp:
            conf = configparser.ConfigParser()
            conf.readfp(fp)
            
            self.COM = conf.get('general', 'COMport')
            self.gain = conf.getfloat("rtlsdr", "gain")
            self.sample_rate = conf.getfloat("rtlsdr", "sample_rate")
            self.BandWidth = conf.getfloat("rtlsdr", "BandWidth")

            self.path = conf.get("log", "path")
            self.distance = conf.getfloat("log", "distance")
            self.spliter = conf.getboolean("log", "spliter")
        

            self.freqlist = []

            for i in range(1,7):
                self.freqlist.append(conf.getfloat("freqs", f"freq{i}"))

    def set_freqs(self, listvalue):
        self.freqlist = []
        for freq in listvalue:
            self.freqlist.append(freq['freq'])

    def save(self):
        conf = configparser.ConfigParser()

        conf.add_section("general")
        conf.add_section("rtlsdr")
        conf.add_section("log")
        conf.add_section("freqs")

        conf.set('general', 'COMport', self.COM)

        conf.set("rtlsdr", "gain", str(self.gain))
        conf.set("rtlsdr", "sample_rate", str(self.sample_rate))
        conf.set("rtlsdr", "BandWidth", str(self.BandWidth))

        conf.set("log", "path", self.path)
        conf.set("log", "distance", str(self.distance))
        conf.set("log", "spliter", str(self.spliter))

        cnt = 1
        for freq in self.freqlist:
            conf.set("freqs", f"freq{cnt}", str(freq))
            cnt += 1

        with open(self.configpath, "w", encoding="utf-8") as fp:
            conf.write(fp)

        print('savaed')


'''
t = config('./config.ini')
t.read()
p = t.freqlist
k = []

for tt in p:
    k.append({'freq': tt + 12})
t.set_freqs(k)

t.save()

conf.read(conf_file_path)

section_list = conf.sections()
conf.has_section("section_name")


opt_val_list = conf.items("rtlsdr")
print(opt_val_list)
#train_path = conf.get("rtlsdr", "option_name")
'''