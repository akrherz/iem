'''
   + Relative Humidity  
   + Temperature
   + Snowfall
   + Precipitation
   + Wind Chill and Heat Index summaries
   + Number of rainy days
   + Some measure of sun and clouds
'''
from pyiem.datatypes import temperature
import pyiem.meteorology as met
import psycopg2
import numpy as np
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

climate = {}
ccursor.execute("""
  SELECT valid, high, low from climate51 where
  station = 'IA0200'
  """)
for row in ccursor:
    climate[ row[0].strftime("%m%d") ] = {'high': row[1], 'low': row[2]}

# Snow and Precip obs
ccursor.execute("""
  SELECT day, precip, snow from alldata_ia where
  station = 'IA0200' and day >= '2009-01-01' ORDER by day ASC
  """)

out = open('wxdata.txt', 'w')
out.write('YEAR,MONTH,DAY,AVGT,RELH,TEMP,SNOW,PRECIP,HEAT,WINDCHILL,CLOUDY\n')

for row in ccursor:
    day = row[0]

    acursor.execute("""SELECT valid, tmpf, dwpf, sknt, skyc1, skyc2, skyc3 from
    alldata where station = 'AMW' and valid BETWEEN '%s 00:00' and '%s 23:59' 
    and tmpf > -30 and dwpf > -30
  """ % (day.strftime("%Y-%m-%d"),day.strftime("%Y-%m-%d")))
    relh = []
    tmpf = []
    heat = 'N'
    windchill = 'N'
    clcount = 0
    for row2 in acursor:
        t = temperature(row2[1], 'F')
        td = temperature(row2[2], 'F')

        
        if met.heatindex(t, td).value('F') > 90:
            heat = 'Y'
            if t.value('F') < 50:
                print t.value('F'), td.value('F'), met.heatindex(t, td).value('F')
        if row2[1] < 32 and row2[3] > 10:
            windchill = 'Y' #approx
        
        sky = 'Clear'
        if 'OVC' in [row2[4], row2[5], row2[6]]:
            sky = 'Overcast'
        elif 'BKN' in [row2[4], row2[5], row2[6]]:
            sky = 'Broken'
        elif 'FEW' in [row2[4], row2[5], row2[6]]:
            sky = 'Fair Skies'
        if row2[0].hour > 7 and row2[0].hour < 18:
            relh.append( met.relh(t,td).value('%') )
            tmpf.append( row2[1] )
            if sky in ['Overcast', 'Broken']:
                clcount += 1

    cloudy = 'N'
    if clcount > 4:
        cloudy = 'Y'
    relh = np.array(relh)
    tmpf = np.array(tmpf)
    avgrelh = np.average(relh)
    avgtmpf = np.average(tmpf)
    climatetmpf = (climate[day.strftime("%m%d")]['high'] + 
                climate[day.strftime("%m%d")]['low']) / 2.0
    T = 'BELOW'
    if avgtmpf > climatetmpf:
        T = "ABOVE"

    snow = "N"
    if row[2] > 0:
        snow = "Y"

    precip = "N"
    if row[1] > 0:
        precip = "Y"

    out.write("%s,%s,%s,%.1f,%.1f,%s,%s,%s,%s,%s,%s\n" % (day.year, day.month, 
                                    day.day, avgtmpf, avgrelh,
                                    T, snow, precip, heat, windchill, cloudy))

out.close()

