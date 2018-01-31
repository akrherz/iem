"""Suck in MADIS data into the iemdb"""
from __future__ import print_function
import time
import datetime
import os
import sys
import subprocess

import netCDF4
import pytz
import psycopg2.extras
import metpy.calc as mcalc
from metpy.units import units
from pyiem.observation import Observation
from pyiem.datatypes import temperature, distance, speed
from pyiem.util import get_dbconn

MY_PROVIDERS = ["KYTC-RWIS",
                "KYMN",
                "NEDOR",
                "MesoWest"]


def find_file():
    """Find the most recent file"""
    fn = None
    for i in range(0, 4):
        ts = datetime.datetime.utcnow() - datetime.timedelta(hours=i)
        testfn = ts.strftime("/mesonet/data/madis/mesonet1/%Y%m%d_%H00.nc")
        if os.path.isfile(testfn):
            fn = testfn
            break

    if fn is None:
        sys.exit()
    return fn


def sanity_check(val, lower, upper, defaultval):
    """Simple bounds check"""
    if val > lower and val < upper:
        return float(val)
    return defaultval


def provider2network(provider):
    """ Convert a MADIS network ID to one that I use, here in IEM land"""
    if provider in ['KYMN']:
        return provider
    if provider == 'MesoWest':
        return 'VTWAC'
    if len(provider) == 5 or provider in ['KYTC-RWIS', 'NEDOR']:
        if provider[:2] == 'IA':
            return None
        return '%s_RWIS' % (provider[:2],)
    print("Unsure how to convert %s into a network" % (provider,))
    return None


def main():
    """Do Something"""
    pgconn = get_dbconn('iem')
    icursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    fn = find_file()
    try:
        nc = netCDF4.Dataset(fn)
    except Exception as _:
        # File may be in progress of being read, wait a little bit
        time.sleep(20)
        nc = netCDF4.Dataset(fn)

    stations = nc.variables["stationId"][:]
    providers = nc.variables["dataProvider"][:]
    names = nc.variables["stationName"][:]
    tmpk = nc.variables["temperature"][:]
    dwpk = nc.variables["dewpoint"][:]
    relh = mcalc.relative_humidity_from_dewpoint(tmpk * units.degK,
                                                 dwpk * units.degK
                                                 ).magnitude * 100.
    tmpk_dd = nc.variables["temperatureDD"][:]
    obtime = nc.variables["observationTime"][:]
    pressure = nc.variables["stationPressure"][:]
    # altimeter = nc.variables["altimeter"][:]
    # slp = nc.variables["seaLevelPressure"][:]
    drct = nc.variables["windDir"][:]
    smps = nc.variables["windSpeed"][:]
    gmps = nc.variables["windGust"][:]
    # gmps_drct = nc.variables["windDirMax"][:]
    pcpn = nc.variables["precipAccum"][:]
    rtk1 = nc.variables["roadTemperature1"][:]
    rtk2 = nc.variables["roadTemperature2"][:]
    rtk3 = nc.variables["roadTemperature3"][:]
    rtk4 = nc.variables["roadTemperature4"][:]
    subk1 = nc.variables["roadSubsurfaceTemp1"][:]

    db = {}

    for recnum, provider in enumerate(providers):
        this_provider = provider.tostring().replace('\x00', '')
        this_station = stations[recnum].tostring().replace('\x00', '')
        if (not this_provider.endswith('DOT') and
                this_provider not in MY_PROVIDERS):
            continue
        name = names[recnum].tostring(
            ).replace("'",  "").replace('\x00', '').replace('\xa0',
                                                            ' ').strip()
        if name == '':
            continue
        if this_provider == 'MesoWest':
            # get the network from the last portion of the name
            network = name.split()[-1]
            if network != 'VTWAC':
                continue
        else:
            network = provider2network(this_provider)
        if network is None:
            continue
        db[this_station] = {}
        ticks = obtime[recnum]
        ts = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=ticks)
        db[this_station]['ts'] = ts.replace(tzinfo=pytz.utc)
        db[this_station]['network'] = network
        db[this_station]['pres'] = sanity_check(pressure[recnum], 0, 1000000,
                                                -99)
        db[this_station]['tmpk'] = sanity_check(tmpk[recnum], 0, 500, -99)
        db[this_station]['dwpk'] = sanity_check(dwpk[recnum], 0, 500, -99)
        db[this_station]['tmpk_dd'] = tmpk_dd[recnum]
        db[this_station]['relh'] = relh[recnum]
        db[this_station]['drct'] = sanity_check(drct[recnum], -1, 361, -99)
        db[this_station]['smps'] = sanity_check(smps[recnum], -1, 200, -99)
        db[this_station]['gmps'] = sanity_check(gmps[recnum], -1, 200, -99)
        db[this_station]['rtk1'] = sanity_check(rtk1[recnum], 0, 500, -99)
        db[this_station]['rtk2'] = sanity_check(rtk2[recnum], 0, 500, -99)
        db[this_station]['rtk3'] = sanity_check(rtk3[recnum], 0, 500, -99)
        db[this_station]['rtk4'] = sanity_check(rtk4[recnum], 0, 500, -99)
        db[this_station]['subk'] = sanity_check(subk1[recnum], 0, 500, -99)
        db[this_station]['pday'] = sanity_check(pcpn[recnum], -1, 5000, -99)

    for sid in db:
        # print("Processing %s[%s]" % (sid, db[sid]['network']))
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
        if db[sid]['relh'] >= 0:
            iem.data['relh'] = float(db[sid]['relh'])
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
            iem.data['rwis_subf'] = temperature(db[sid]['subk'],
                                                'K').value('F')
        if db[sid]['pday'] >= 0:
            iem.data['pday'] = round(distance(db[sid]['pday'],
                                              'MM').value("IN"),
                                     2)
        if not iem.save(icursor):
            print(("MADIS Extract: %s found new station: %s network: %s"
                  "") % (fn.split("/")[-1], sid, db[sid]['network']))
            subprocess.call("python sync_stations.py %s" % (fn,), shell=True)
            os.chdir("../../dbutil")
            subprocess.call("sh SYNC_STATIONS.sh", shell=True)
            os.chdir("../ingestors/madis")
            print("...done with sync.")
        del iem
    nc.close()
    icursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == '__main__':
    main()
