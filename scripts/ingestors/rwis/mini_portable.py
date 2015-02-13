"""Process data from the mini and portables """

import datetime
import pytz
import psycopg2.extras
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
from pyiem.tracker import TrackerEngine
from pyiem.observation import Observation
from pyiem.datatypes import temperature, humidity
import pyiem.meteorology as meteorology
from pyiem.network import Table as NetworkTable
nt = NetworkTable("IA_RWIS")

lkp = {'miniExportM1.csv': 'RAII4',
       'miniExportM2.csv': 'RMYI4',
       'portableExportP1.csv': 'RSWI4',
       'portableExportP2.csv': 'RAGI4',
       'portableExportP3.csv': 'RLMI4',
       # 'portableExportPT.csv': 'ROCI4',
       'portableExportPT.csv': 'RRCI4',
       'miniExportIFB.csv': 'RIFI4',
       }

thres = datetime.datetime.utcnow() - datetime.timedelta(minutes=180)
thres = thres.replace(tzinfo=pytz.timezone("UTC"))


def processfile( fp ):
    o = open("/mesonet/data/incoming/rwis/%s" % (fp,), 'r').readlines()
    if len(o) < 2:
        return
    heading = o[0].split(",")
    cols = o[1].split(",")
    data = {}
    if len(cols) < len(heading):
        return
    for i in range(len(heading)):
        if cols[i].strip() != "/":
            data[heading[i].strip()] = cols[i].strip()

    nwsli = lkp[fp]
    if fp in ['portableExportP1.csv', 'miniExportIFB.csv']:
        ts = datetime.datetime.strptime(data['date_time'][:16],
                                        '%Y-%m-%d %H:%M')
    else:
        ts = datetime.datetime.strptime(data['date_time'][:-6],
                                        '%Y-%m-%d %H:%M')
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    iem = Observation(nwsli, 'IA_RWIS', ts)
    if ts.year < 2010:
        print(("rwis/mini_portable.py file: %s bad timestamp: %s"
               "") % (fp, data['date_time']))
        return
    iem.load(icursor)

    # IEM Tracker stuff is missing

    if data.get('wind_speed', '') != '':
        iem.data['sknt'] = float(data['wind_speed']) * 1.17
    if data.get('sub', '') != '':
        iem.data['rwis_subf'] = float(data['sub'])
    if data.get('air_temp', '') != '':
        iem.data['tmpf'] = float(data['air_temp'])
    if data.get('pave_temp', '') != '':
        iem.data['tsf0'] = float(data['pave_temp'])
    if data.get('pave_temp2', '') != '':
        iem.data['tsf1'] = float(data['pave_temp2'])
    if data.get('press', '') != '':
        iem.data['alti'] = float(data['press'])
    if data.get('RH', '') != '':
        if float(data['RH']) > 1:
            t = temperature(iem.data['tmpf'], 'F')
            rh = humidity(float(data['RH']), '%')
            iem.data['dwpf'] = meteorology.dewpoint(t, rh).value('F')
    if data.get('wind_dir', '') != '':
        iem.data['drct'] = float(data['wind_dir'])
    iem.save(icursor)

for k in lkp.keys():
    processfile(k)


IEM.commit()
