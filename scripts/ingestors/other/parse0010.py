"""ISU Agronomy Hall Vantage Pro 2 OT0010"""
import datetime
import re
import os
import sys
import pytz
from pyiem.datatypes import speed
from pyiem.observation import Observation
import psycopg2
iemaccess = psycopg2.connect(database='iem', host='iemdb')
cursor = iemaccess.cursor()

valid = datetime.datetime.utcnow()
valid = valid.replace(tzinfo=pytz.timezone("UTC"))
valid = valid.astimezone(pytz.timezone("America/Chicago"))
fn = valid.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/text/ot/ot0010.dat")

if not os.path.isfile(fn):
    sys.exit(0)

lines = open(fn, "r").readlines()
lastLine = lines[-1].strip()
tokens = re.split("[\s+]+", lastLine)
if len(tokens) != 20:
    sys.exit(0)

tparts = re.split(":", tokens[3])
valid = valid.replace(hour=int(tparts[0]),
                      minute=int(tparts[1]), second=0, microsecond=0)

iem = Observation("OT0010", "OT", valid)

sknt = speed(float(tokens[8]), 'MPH').value('KT')

iem.data['tmpf'] = float(tokens[4])
iem.data['max_tmpf'] = float(tokens[5])
iem.data['min_tmpf'] = float(tokens[6])
iem.data['relh'] = int(tokens[7])
iem.data['sknt'] = speed(float(tokens[8]), 'mph').value('KT')
iem.data['drct'] = int(tokens[9])
iem.data['max_sknt'] = speed(float(tokens[10]), 'mph').value('KT')
iem.data['alti'] = float(tokens[12])
iem.data['pday'] = float(tokens[13])


iem.save(cursor)

cursor.close()
iemaccess.commit()
