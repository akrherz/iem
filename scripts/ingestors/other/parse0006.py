import datetime
from pyiem.observation import Observation
import pytz
import os
import sys
import pyiem.meteorology as meteorology
from pyiem.datatypes import temperature, humidity, speed
import psycopg2
IEM = psycopg2.connect("host=iemdb dbname=iem")
icursor = IEM.cursor()

now = datetime.datetime.now().replace(tzinfo=pytz.timezone("America/Chicago"))

fn = ("/mesonet/ARCHIVE/data/%s/text/ot/ot0006.dat"
      "") % (now.strftime("%Y/%m/%d"), )

if not os.path.isfile(fn):
    sys.exit(0)
lines = open(fn, 'r').readlines()
line = lines[-1]

# January 17, 2017 02:57 PM
# 35.1 35.8 33.4 92 3 351 14 2:13PM 30.03 0.00 1.12 1.12 68.6 36
tokens = line.split(" ")
if len(tokens) != 19:
    sys.exit(0)

ts = datetime.datetime.strptime(" ".join(tokens[:5]),
                                "%B %d, %Y %I:%M %p")

ts = now.replace(year=ts.year, month=ts.month, day=ts.day, hour=ts.hour,
                 minute=ts.minute)

iemob = Observation("OT0006", "OT", ts)

iemob.data['tmpf'] = float(tokens[5])
iemob.data['relh'] = float(tokens[8])
tmpf = temperature(iemob.data['tmpf'], 'F')
relh = humidity(iemob.data['relh'], '%')
iemob.data['dwpf'] = meteorology.dewpoint(tmpf, relh).value('F')
iemob.data['sknt'] = speed(float(tokens[9]), 'MPH').value('KT')
iemob.data['drct'] = tokens[10]
iemob.data['alti'] = float(tokens[13])
iemob.data['pday'] = float(tokens[14])
iemob.save(icursor)

icursor.close()
IEM.commit()
IEM.close()
