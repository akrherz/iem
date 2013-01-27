import datetime
from pyiem.observation import Observation
import pytz
import os
import sys
import mesonet
import psycopg2
IEM = psycopg2.connect("host=iemdb dbname=iem user=nobody")
icursor = IEM.cursor()

now = datetime.datetime.now()

fp = "/mesonet/ARCHIVE/data/%s/text/ot/ot0007.dat" % (now.strftime("%Y/%m/%d"),)

if (not os.path.isfile(fp)):
    sys.exit(0)

lines = open(fp, 'r').readlines()
line = lines[-1]

# 114,2006,240,1530,18.17,64.70, 88.9,2.675,21.91,1014.3,0.000
tokens = line.split(",")
if (len(tokens) != 11):
    sys.exit(0)
hhmm = "%04i" % (int(tokens[3]),)
ts = now.replace(hour= int(hhmm[:2]), minute= int(hhmm[2:]), second = 0,
                 microsecond=0 , tzinfo=pytz.timezone("America/Chicago"))

iemob = Observation("OT0007", "OT", ts)

iemob.data['tmpf'] = tokens[5]
iemob.data['relh'] = tokens[6]
iemob.data['dwpf'] = mesonet.dwpf(float(iemob.data['tmpf']), float(iemob.data['relh']) )
iemob.data['sknt'] = float(tokens[7]) * 1.94
iemob.data['drct'] = tokens[8]
iemob.data['pres'] = float(tokens[9]) / 960 * 28.36
iemob.save(icursor)

icursor.close()
IEM.commit()
IEM.close()

