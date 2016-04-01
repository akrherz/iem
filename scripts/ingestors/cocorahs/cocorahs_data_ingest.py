# Process CoCoRaHS Stations!

import sys
import urllib2
import datetime
import psycopg2
import pytz
from pyiem.observation import Observation
dbconn = psycopg2.connect(database='iem', host='iemdb')
cursor = dbconn.cursor()

now = datetime.datetime.now() - datetime.timedelta(hours=3)

lts = datetime.datetime.utcnow()
lts = lts.replace(tzinfo=pytz.timezone("UTC"))
lts = lts.astimezone(pytz.timezone("America/Chicago"))

state = sys.argv[1]

url = ("http://data.cocorahs.org/Cocorahs/export/exportreports.aspx"
       "?ReportType=Daily&dtf=1&Format=CSV&State=%s&ReportDateType=timestamp&"
       "Date=%s&TimesInGMT=False") % (state,
                                      now.strftime("%m/%d/%Y%%20%H:00%%20%P"))
req = urllib2.Request(url)
data = urllib2.urlopen(req, timeout=30).readlines()


# Process Header
header = {}
h = data[0].split(",")
for i in range(len(h)):
    header[h[i]] = i

if 'StationNumber' not in header:
    sys.exit()


def safeP(v):
    v = v.strip()
    if v == "T":
        return 0.0001
    if v == "NA":
        return -99
    return float(v)

for row in data[1:]:
    cols = row.split(",")
    sid = cols[header["StationNumber"]].strip()

    t = "%s %s" % (cols[header["ObservationDate"]],
                   cols[header["ObservationTime"]].strip())
    ts = datetime.datetime.strptime(t, "%Y-%m-%d %I:%M %p")
    lts = lts.replace(year=ts.year, month=ts.month, day=ts.day,
                      hour=ts.hour, minute=ts.minute)
    iem = Observation(sid, "%sCOCORAHS" % (state,), lts)
    iem.data['pday'] = safeP(cols[header["TotalPrecipAmt"]])
    if cols[header["NewSnowDepth"]].strip() != "NA":
        iem.data['snow'] = safeP(cols[header["NewSnowDepth"]])
    if cols[header["TotalSnowDepth"]].strip() != "NA":
        iem.data['snowd'] = safeP(cols[header["TotalSnowDepth"]])
    iem.save(cursor)
    del iem

cursor.close()
dbconn.commit()
