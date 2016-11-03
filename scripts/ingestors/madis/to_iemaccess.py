"""Suck in MADIS data into the iemdb"""
import netCDF4
import datetime
import os
import sys
from pyiem.observation import Observation
from pyiem.datatypes import temperature, distance, speed
import subprocess
import pytz
import psycopg2.extras
pgconn = psycopg2.connect(database='iem', host='iemdb')
icursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

fn = None
for i in range(0, 4):
    ts = datetime.datetime.utcnow() - datetime.timedelta(hours=i)
    testfn = ts.strftime("/mesonet/data/madis/mesonet1/%Y%m%d_%H00.nc")
    if os.path.isfile(testfn):
        fn = testfn
        break

if fn is None:
    sys.exit()

try:
    nc = netCDF4.Dataset(fn)
except:
    # File may be in progress of being read, wait a little bit
    import time
    time.sleep(20)
    nc = netCDF4.Dataset(fn)


def sanityCheck(val, lower, upper, rt):
    if val > lower and val < upper:
        return float(val)
    return rt

stations = nc.variables["stationId"][:]
providers = nc.variables["dataProvider"][:]
names = nc.variables["stationName"][:]
tmpk = nc.variables["temperature"][:]
tmpk_dd = nc.variables["temperatureDD"][:]
obTime = nc.variables["observationTime"][:]
pressure = nc.variables["stationPressure"][:]
altimeter = nc.variables["altimeter"][:]
slp = nc.variables["seaLevelPressure"][:]
dwpk = nc.variables["dewpoint"][:]
drct = nc.variables["windDir"][:]
smps = nc.variables["windSpeed"][:]
gmps = nc.variables["windGust"][:]
gmps_drct = nc.variables["windDirMax"][:]
pcpn = nc.variables["precipAccum"][:]
rtk1 = nc.variables["roadTemperature1"][:]
rtk2 = nc.variables["roadTemperature2"][:]
rtk3 = nc.variables["roadTemperature3"][:]
rtk4 = nc.variables["roadTemperature4"][:]
subk1 = nc.variables["roadSubsurfaceTemp1"][:]

db = {}

MY_PROVIDERS = ["AKDOT",
                "CODOT",
                "DEDOT",
                "FLDOT",
                "GADOT",
                "INDOT",
                "KSDOT",
                "KYTC-RWIS",
                "KYMN",
                "MADOT",
                "MEDOT",
                "MIDOT",
                "MDDOT",
                "MNDOT",
                "MODOT",
                "NEDOR",
                "NHDOT",
                "NDDOT",
                "NVDOT",
                "OHDOT",
                "WIDOT",
                "WVDOT",
                "WYDOT",
                "VADOT",
                "VTDOT",
                "MesoWest"
                ]


def provider2network(p):
    """ Convert a MADIS network ID to one that I use, here in IEM land"""
    if p in ['KYMN']:
        return p
    if p == 'MesoWest':
        return 'VTWAC'
    return '%s_RWIS' % (p[:2],)

for recnum in range(len(providers)):
    thisProvider = providers[recnum].tostring().replace('\x00', '')
    thisStation = stations[recnum].tostring().replace('\x00', '')
    if thisProvider not in MY_PROVIDERS:
        continue
    name = names[recnum].tostring().replace("'",
                                            "").replace('\x00',
                                                        '').replace('\xa0',
                                                                    ' '
                                                                    ).strip()
    if thisProvider == 'MesoWest':
        # get the network from the last portion of the name
        network = name.split()[-1]
        if network != 'VTWAC':
            continue
    else:
        network = provider2network(thisProvider)
    db[thisStation] = {}
    ticks = obTime[recnum]
    ts = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=ticks)
    db[thisStation]['ts'] = ts.replace(tzinfo=pytz.timezone('UTC'))
    db[thisStation]['network'] = network
    db[thisStation]['pres'] = sanityCheck(pressure[recnum], 0, 1000000, -99)
    db[thisStation]['tmpk'] = sanityCheck(tmpk[recnum], 0, 500, -99)
    db[thisStation]['dwpk'] = sanityCheck(dwpk[recnum], 0, 500, -99)
    db[thisStation]['tmpk_dd'] = tmpk_dd[recnum]
    db[thisStation]['drct'] = sanityCheck(drct[recnum], -1, 361, -99)
    db[thisStation]['smps'] = sanityCheck(smps[recnum], -1, 200, -99)
    db[thisStation]['gmps'] = sanityCheck(gmps[recnum], -1, 200, -99)
    db[thisStation]['rtk1'] = sanityCheck(rtk1[recnum], 0, 500, -99)
    db[thisStation]['rtk2'] = sanityCheck(rtk2[recnum], 0, 500, -99)
    db[thisStation]['rtk3'] = sanityCheck(rtk3[recnum], 0, 500, -99)
    db[thisStation]['rtk4'] = sanityCheck(rtk4[recnum], 0, 500, -99)
    db[thisStation]['subk'] = sanityCheck(subk1[recnum], 0, 500, -99)
    db[thisStation]['pday'] = sanityCheck(pcpn[recnum], -1, 5000, -99)

for sid in db.keys():
    iem = Observation(sid, db[sid]['network'], db[sid]['ts'])
    # if not iem.load(icursor):
    #    print 'Missing fp: %s network: %s station: %s' % (fp,
    #                                                      db[sid]['network'],
    #                                                      sid)
    #    subprocess.call("python sync_stations.py %s" % (fp,), shell=True)
    #    os.chdir("../../dbutil")
    #    subprocess.call("sh SYNC_STATIONS.sh", shell=True)
    #    os.chdir("../ingestors/madis")
    iem.data['tmpf'] = temperature(db[sid]['tmpk'], 'K').value('F')
    iem.data['dwpf'] = temperature(db[sid]['dwpk'], 'K').value('F')
    if db[sid]['drct'] >= 0:
        iem.data['drct'] = db[sid]['drct']
    if db[sid]['smps'] >= 0:
        iem.data['sknt'] = speed(db[sid]['smps'], 'MPS').value('KT')
    if db[sid]['gmps'] >= 0:
        iem.data['gust'] = speed(db[sid]['gmps'], 'MPS').value('KT')
    if db[sid]['pres'] > 0:
        iem.data['pres'] = (float(db[sid]['pres']) / 100.00) * 0.02952
    if db[sid]['rtk1'] > 0:
        iem.data['tsf0'] = temperature(db[sid]['rtk1'], 'K').value('F')
    if db[sid]['rtk2'] > 0:
        iem.data['tsf1'] = temperature(db[sid]['rtk2'], 'K').value('F')
    if db[sid]['rtk3'] > 0:
        iem.data['tsf2'] = temperature(db[sid]['rtk3'], 'K').value('F')
    if db[sid]['rtk4'] > 0:
        iem.data['tsf3'] = temperature(db[sid]['rtk4'], 'K').value('F')
    if db[sid]['subk'] > 0:
        iem.data['rwis_subf'] = temperature(db[sid]['subk'], 'K').value('F')
    if db[sid]['pday'] >= 0:
        iem.data['pday'] = round(distance(db[sid]['pday'], 'MM').value("IN"),
                                 2)
    if not iem.save(icursor):
        print(("MADIS Extract: %s found new station: %s network: %s"
              "") % (fn.split("/")[-1], sid, db[sid]['network']))
        subprocess.call("python sync_stations.py %s" % (fn,), shell=True)
        os.chdir("../../dbutil")
        subprocess.call("sh SYNC_STATIONS.sh", shell=True)
        os.chdir("../ingestors/madis")
        print("...done with sync.")
    del(iem)
nc.close()
icursor.close()
pgconn.commit()
pgconn.close()
