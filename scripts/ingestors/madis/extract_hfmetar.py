"""Pull in what's available for HFMETAR MADIS data

Run from RUN_10MIN.sh
Run from RUN_40_AFTER.sh for two hours ago
"""
from __future__ import print_function
import os
import sys
import re
import datetime
import warnings

import pytz
import netCDF4
import numpy as np
from metar import Metar
from pyiem.datatypes import temperature, distance, pressure, speed
from pyiem.observation import Observation
from pyiem.util import get_dbconn
from pyiem.reference import TRACE_VALUE

warnings.simplefilter('ignore', RuntimeWarning)


def vsbyfmt(val):
    """ Tricky formatting of vis"""
    if val == 0:
        return 0
    if val <= 0.125:
        return "1/8"
    if val <= 0.25:
        return "1/4"
    if val <= 0.375:
        return "3/8"
    if val <= 0.5:
        return "1/2"
    if val <= 1.1:
        return "1"
    if val <= 1.6:
        return "1 1/2"
    if val <= 2.1:
        return "2"
    if val <= 2.6:
        return "2 1/2"
    return int(val)


def tostring(val):
    """Save tostring"""
    return re.sub('\x00', '', val.tostring()).strip()


def process(ncfn):
    """Process this file """
    pgconn = get_dbconn('iem')
    icursor = pgconn.cursor()
    xref = {}
    icursor.execute("""SELECT id, network from stations where
    network ~* 'ASOS' or network = 'AWOS' and country = 'US'""")
    for row in icursor:
        xref[row[0]] = row[1]
    icursor.close()
    nc = netCDF4.Dataset(ncfn)
    data = {}
    for vname in ['stationId', 'observationTime', 'temperature', 'dewpoint',
                  'altimeter',  # Pa
                  'windDir',
                  'windSpeed',  # mps
                  'windGust', 'visibility',  # m
                  'precipAccum', 'presWx', 'skyCvr',
                  'skyCovLayerBase', 'autoRemark', 'operatorRemark']:
        data[vname] = nc.variables[vname][:]
        vname += "QCR"
        if vname in nc.variables:
            data[vname] = nc.variables[vname][:]
    for vname in ['temperature', 'dewpoint']:
        data[vname+"C"] = temperature(data[vname], 'K').value('C')
        data[vname] = temperature(data[vname], 'K').value('F')
    for vname in ['windSpeed', 'windGust']:
        data[vname] = speed(data[vname], 'MPS').value('KT')

    data['altimeter'] = pressure(data['altimeter'], 'PA').value("IN")
    data['skyCovLayerBase'] = distance(data['skyCovLayerBase'],
                                       'M').value("FT")
    data['visibility'] = distance(data['visibility'],
                                  'M').value("MI")
    data['precipAccum'] = distance(data['precipAccum'],
                                   'MM').value("IN")

    for i in range(len(data['stationId'])):
        sid = tostring(data['stationId'][i])
        sid3 = sid[1:] if sid[0] == 'K' else sid
        ts = datetime.datetime(1970, 1, 1) + datetime.timedelta(
                seconds=data['observationTime'][i])
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))

        mtr = "%s %sZ AUTO " % (sid, ts.strftime("%d%H%M"))
        network = xref.get(sid3, 'ASOS')
        iem = Observation(sid3, network, ts)
        #  06019G23KT
        if (data['windDirQCR'][i] == 0 and
                data['windDir'][i] is not np.ma.masked):
            iem.data['drct'] = int(data['windDir'][i])
            mtr += "%03i" % (iem.data['drct'], )
        else:
            mtr += "///"

        if (data['windSpeedQCR'][i] == 0 and
                data['windSpeed'][i] is not np.ma.masked):
            iem.data['sknt'] = int(data['windSpeed'][i])
            mtr += "%02i" % (iem.data['sknt'], )
        else:
            mtr += "//"

        if (data['windGustQCR'][i] == 0 and
                data['windGust'][i] is not np.ma.masked and
                data['windGust'][i] > 0):
            iem.data['gust'] = int(data['windGust'][i])
            mtr += "G%02i" % (iem.data['gust'],)
        mtr += "KT "

        if (data['visibilityQCR'][i] == 0 and
                data['visibility'][i] is not np.ma.masked):
            iem.data['vsby'] = float(data['visibility'][i])
            mtr += "%sSM " % (vsbyfmt(iem.data['vsby']), )

        presentwx = tostring(data['presWx'][i])
        if presentwx != '':
            iem.data['presentwx'] = presentwx
            mtr += "%s " % (presentwx,)

        for _i, (_c, _l) in enumerate(
                        zip(data['skyCvr'][i], data['skyCovLayerBase'][i])):
            if tostring(_c) != '':
                skyc = tostring(_c)
                iem.data['skyc%s' % (_i+1,)] = skyc
                if skyc != 'CLR':
                    iem.data['skyl%s' % (_i+1,)] = int(_l)
                    mtr += "%s%03i " % (tostring(_c), int(_l) / 100)
                else:
                    mtr += "CLR "

        t = ""
        tgroup = "T"
        if (data['temperatureQCR'][i] == 0 and
                data['temperature'][i] is not np.ma.masked):
            # iem.data['tmpf'] = float(data['temperature'][i])
            tmpc = float(data['temperatureC'][i])
            t = "%s%02i/" % ("M" if tmpc < 0 else "",
                             tmpc if tmpc > 0 else (0 - tmpc))
            tgroup += "%s%03i" % ("1" if tmpc < 0 else "0",
                                  (tmpc if tmpc > 0 else (0 - tmpc)) * 10.)
        if (data['dewpointQCR'][i] == 0 and
                data['dewpoint'][i] is not np.ma.masked):
            # iem.data['dwpf'] = float(data['dewpoint'][i])
            tmpc = float(data['dewpointC'][i])
            if t != "":
                t = "%s%s%02i " % (t, "M" if tmpc < 0 else "",
                                   tmpc if tmpc > 0 else 0 - tmpc)
                tgroup += "%s%03i" % ("1" if tmpc < 0 else "0",
                                      (tmpc if tmpc > 0 else (0 - tmpc)) * 10.)
        if len(t) > 4:
            mtr += t
        if (data['altimeterQCR'][i] == 0 and
                data['altimeter'][i] is not np.ma.masked):
            iem.data['alti'] = round(data['altimeter'][i], 2)
            mtr += "A%4i " % (iem.data['alti'] * 100.,)

        mtr += "RMK "
        if (data['precipAccumQCR'][i] == 0 and
                data['precipAccum'][i] is not np.ma.masked):
            if data['precipAccum'][i] >= 0.01:
                iem.data['phour'] = round(data['precipAccum'][i], 2)
                mtr += "P%04i " % (iem.data['phour'] * 100.,)
            elif data['precipAccum'][i] < 0.01 and data['precipAccum'][i] > 0:
                # Trace
                mtr += "P0000 "
                iem.data['phour'] = TRACE_VALUE

        if tgroup != "T":
            mtr += "%s " % (tgroup, )
        autoremark = tostring(data['autoRemark'][i])
        opremark = tostring(data['operatorRemark'][i])
        if autoremark != '' or opremark != '':
            mtr += "%s %s " % (autoremark, opremark)
        mtr += "MADISHF"
        # Eat our own dogfood
        try:
            Metar.Metar(mtr)
            iem.data['raw'] = mtr
        except Exception as exp:
            pass

        icursor = pgconn.cursor()
        if not iem.save(icursor, force_current_log=True,
                        skip_current=True):
            print(("extract_hfmetar: unknown station? %s %s %s\n%s"
                   ) % (sid3, network, ts, mtr))

        icursor.close()
        pgconn.commit()


def find_fn(argv):
    """Figure out which file to run for"""
    if len(argv) == 5:
        utcnow = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]),
                                   int(argv[4]))
        return utcnow.strftime("/mesonet/data/madis/hfmetar/%Y%m%d_%H00.nc")
    else:
        utcnow = datetime.datetime.utcnow()
        start = 0 if len(argv) == 1 else int(argv[1])
        for i in range(start, 5):
            ts = utcnow - datetime.timedelta(hours=i)
            fn = ts.strftime("/mesonet/data/madis/hfmetar/%Y%m%d_%H00.nc")
            if os.path.isfile(fn):
                return fn
        sys.exit()


def main(argv):
    """Do Something"""
    fn = find_fn(argv)
    process(fn)


if __name__ == '__main__':
    main(sys.argv)
