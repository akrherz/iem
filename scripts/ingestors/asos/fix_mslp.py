'''
 Fix MSLP in the database by reprocessing the stored METAR...
'''
from pyIEM import iemdb, mesonet
i = iemdb.iemdb()
asos = i['asos']
mesosite = i['mesosite']
import mx.DateTime, csv, time
import sys
import os
from metar import Metar
import psycopg2
ASOS = psycopg2.connect('dbname=asos host=iemdb')
acursor = ASOS.cursor()
acursor2 = ASOS.cursor()

acursor.execute("""SELECT valid, station, metar from t2011 WHERE 
    station = 'PVD' and mslp is null and metar is not null""")

fix = 0
for row in acursor:
    mstring = " ".join(row[2].strip().split())
    try:
        mtr = Metar.Metar(mstring, row[0].month, row[0].year)
    except:
        print 'BAD METAR'
        continue
    if mtr.press_sea_level:
        acursor2.execute("""UPDATE t2011 SET mslp = %s, metar = %s 
           where station = %s and valid = %s""", (mtr.press_sea_level.value("MB"), 
                                                  mstring, row[1], row[0]))
        if acursor2.rowcount != 1:
            print 'BAD UPDATE', acursor2.rowcount
        fix += 1

print acursor.rowcount, fix
acursor2.close()
ASOS.commit()
ASOS.close()

