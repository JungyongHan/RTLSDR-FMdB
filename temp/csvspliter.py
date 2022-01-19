import csv
import math
import pandas as pd
def calcu(record_lat, record_lon, nLatitude, nLongitude):
    #https://janakiev.com/blog/gps-points-distance-python/
    R = 6372800  # Earth radius in meters
    lat1, lon1 = float(record_lat), float(record_lon)
    lat2, lon2 = float(nLatitude), float(nLongitude)
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

def csvget(path, datalist):
    f = open(path, 'r', encoding='utf-8')
    rdr = csv.reader(f)
    for line in rdr:
        datalist.append(line)
    f.close()
jypath = "C:\\atemp\\jy.csv"
etlpath = "C:\\atemp\\etl.csv"

jylist = []
etlist = []

csvget(jypath, jylist)
csvget(etlpath, etlist)
savelist = []
for etldata in etlist:
    try:
        jycomp = 1e9
        comp_etl_Data = -1
        cov_temp = []
        covert = False
        
        while True:
            if etldata[3] == '':
                etldata[3] = '97.3Mhz'
                covert = True

            for jydata in jylist:
                try:
                    if etldata[3] != jydata[0]:
                        continue

                    buffcomp = calcu(jydata[4], jydata[5], etldata[0], etldata[1])
                    if(jycomp > abs(buffcomp)):
                        jycomp = abs(buffcomp)

                        comp_etl_Data = int(jydata[3])
                        if covert:
                            cov_temp = int(jydata[3])
                except:
                    pass

            if covert :
                etldata[3] = '103.5Mhz'
                jycomp = 1e9
                comp_etl_Data = -1
                covert = False
                continue

            if cov_temp:
                etldata[3] = ''
                if comp_etl_Data < cov_temp:
                    comp_etl_Data = cov_temp

            break

    except Exception as ex:
        print(ex)
        
    
    etldata.append(jycomp)
    '''
    if comp_etl_Data < 20:
        comp_etl_Data = "불량"
    elif comp_etl_Data < 30:
        comp_etl_Data = "강잡음"
    elif comp_etl_Data < 40:
        comp_etl_Data = "약잡음"
    else:
        comp_etl_Data = "양호"
    '''
    etldata.append(comp_etl_Data)
    
    savelist.append(etldata)
    print(etldata)

dataframe = pd.DataFrame(savelist)
dataframe.to_csv("C:\\atemp\\tt.csv",header=False,index=False)
'''
    buffcomp = calcu(jydata[4], jydata[5], etldata[0], etldata[1])
    if(jycomp > abs(buffcomp)):
        jycomp = abs(buffcomp)
        comp_etl_Data = etldata[2]

for idx, jydata in enumerate(jylist):
    # 0:97.3Mhz	1:-24   2:-23	3:26	4:126.808448	5:35.327098 6: etldata
    # 103.5Mhz	-11	-20	6	126.8456713	35.22340017	2020-05-21 1:28

    jycomp = 1e9
    comp_etl_Data = -1

    jydata.append(comp_etl_Data)
    jydata.append(jycomp)
    print(jycomp)
dataframe = pd.DataFrame(jylist)
dataframe.to_csv("C:\\atemp\\tt.csv",header=False,index=False)

'''