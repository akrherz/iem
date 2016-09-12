"""
 Process the GHCN data
 http://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/USC00130200.dly
 http://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt

 ID            1-11   Character
YEAR         12-15   Integer
MONTH        16-17   Integer
ELEMENT      18-21   Character
VALUE1       22-26   Integer
MFLAG1       27-27   Character
QFLAG1       28-28   Character
SFLAG1       29-29   Character
VALUE2       30-34   Integer
MFLAG2       35-35   Character
QFLAG2       36-36   Character
SFLAG2       37-37   Character
  .           .          .
  .           .          .
  .           .          .
VALUE31    262-266   Integer
MFLAG31    267-267   Character
QFLAG31    268-268   Character
SFLAG31    269-269   Character

    PRCP = Precipitation (tenths of mm)
    SNOW = Snowfall (mm)
    SNWD = Snow depth (mm)
    TMAX = Maximum temperature (tenths of degrees C)
    TMIN = Minimum temperature (tenths of degrees C)
"""

import urllib2
import os
import datetime
import numpy as np
import psycopg2
import sys
import re
import netCDF4
from pyiem.datatypes import temperature, distance
from pyiem.network import Table as NetworkTable

COOP = psycopg2.connect(database='coop', host='iemdb')
cursor = COOP.cursor()

BASEDIR = "/mesonet/tmp"
BASE = datetime.date(1850, 1, 1)
TODAY = datetime.date.today()

STCONV = {'WA': '45', 'DE': '07', 'DC': '18', 'WI': '47', 'WV': '46',
          'HI': '51', 'FL': '08', 'WY': '48', 'NH': '27', 'NJ': '28',
          'NM': '29', 'TX': '41', 'LA': '16', 'AK': '50', 'NC': '31',
          'ND': '32', 'NE': '25', 'TN': '40', 'NY': '30', 'PA': '36',
          'PI': '91', 'RI': '37', 'NV': '26', 'VA': '44', 'CO': '05',
          'CA': '04', 'AL': '01', 'AR': '03', 'VT': '43', 'IL': '11',
          'GA': '09', 'IN': '12', 'IA': '13', 'OK': '34', 'AZ': '02',
          'ID': '10', 'CT': '06', 'ME': '17', 'MD': '18', 'MA': '19',
          'OH': '33', 'UT': '42', 'MO': '23', 'MN': '21', 'MI': '20',
          'KS': '14', 'MT': '24', 'MS': '22', 'SC': '38', 'KY': '15',
          'OR': '35', 'SD': '39'}


DATARE = re.compile(r"""
(?P<id>[A-Z0-9]{11})
(?P<year>[0-9]{4})
(?P<month>[0-9]{2})
(?P<element>[A-Z0-9]{4})
(?P<value1>[0-9\- ]{5})(?P<flag1>...)
(?P<value2>[0-9\- ]{5})(?P<flag2>...)
(?P<value3>[0-9\- ]{5})(?P<flag3>...)
(?P<value4>[0-9\- ]{5})(?P<flag4>...)
(?P<value5>[0-9\- ]{5})(?P<flag5>...)
(?P<value6>[0-9\- ]{5})(?P<flag6>...)
(?P<value7>[0-9\- ]{5})(?P<flag7>...)
(?P<value8>[0-9\- ]{5})(?P<flag8>...)
(?P<value9>[0-9\- ]{5})(?P<flag9>...)
(?P<value10>[0-9\- ]{5})(?P<flag10>...)
(?P<value11>[0-9\- ]{5})(?P<flag11>...)
(?P<value12>[0-9\- ]{5})(?P<flag12>...)
(?P<value13>[0-9\- ]{5})(?P<flag13>...)
(?P<value14>[0-9\- ]{5})(?P<flag14>...)
(?P<value15>[0-9\- ]{5})(?P<flag15>...)
(?P<value16>[0-9\- ]{5})(?P<flag16>...)
(?P<value17>[0-9\- ]{5})(?P<flag17>...)
(?P<value18>[0-9\- ]{5})(?P<flag18>...)
(?P<value19>[0-9\- ]{5})(?P<flag19>...)
(?P<value20>[0-9\- ]{5})(?P<flag20>...)
(?P<value21>[0-9\- ]{5})(?P<flag21>...)
(?P<value22>[0-9\- ]{5})(?P<flag22>...)
(?P<value23>[0-9\- ]{5})(?P<flag23>...)
(?P<value24>[0-9\- ]{5})(?P<flag24>...)
(?P<value25>[0-9\- ]{5})(?P<flag25>...)
(?P<value26>[0-9\- ]{5})(?P<flag26>...)
(?P<value27>[0-9\- ]{5})(?P<flag27>...)
(?P<value28>[0-9\- ]{5})(?P<flag28>...)
(?P<value29>[0-9\- ]{5})(?P<flag29>...)
(?P<value30>[0-9\- ]{5})(?P<flag30>...)
(?P<value31>[0-9\- ]{5})(?P<flag31>...)
""", re.VERBOSE)


def get_file(station):
    ''' Download the file from NCDC, if necessary! '''
    # Convert IEM station into what NCDC uses, sigh
    ncdc = "%s%s" % (STCONV[station[:2]], station[2:])
    # IPv6, use 205.167.25.102 rather than www1.ncdc.noaa.gov
    uri = "http://205.167.25.102/pub/data/ghcn/daily/all/USC00%s.dly" % (
                                                                        ncdc)
    localfn = "%s/USC00%s.dly" % (BASEDIR, ncdc)
    if not os.path.isfile(localfn):
        print 'Downloading from NCDC station: %s...' % (ncdc, ),
        try:
            data = urllib2.urlopen(uri)
        except Exception, exp:
            print exp
            return None
        o = open(localfn, 'w')
        o.write(data.read())
        o.close()
        print 'done.'
    else:
        print '%s is cached...' % (localfn,)
    return open(localfn, 'r')


def get_days_for_month(day):
    ''' Compute the number of days this month '''
    nextmo = day + datetime.timedelta(days=35)
    nextmo = nextmo.replace(day=1)
    return (nextmo - day).days


def varconv(val, element):
    ''' Convert NCDC to something we use in the database '''
    if element in ['TMAX', 'TMIN']:
        v = round(temperature(float(val) / 10.0, 'C').value('F'), 0)
        if v < -100 or v > 150:
            return None
        return v
    if element in ['PRCP']:
        v = round((float(val) / 10.0) / 25.4, 2)
        if v < 0:
            return None
        return v
    if element in ['SNOW', 'SNWD']:
        v = round(float(val) / 25.4, 1)
        if v < 0:
            return None
        return v
    return None


def create_netcdf(station, metadata):
    """Create a GHCN netCDF file for other local usage"""
    mydir = "%s/%s" % (BASEDIR, station[:2])
    if not os.path.isdir(mydir):
        os.makedirs(mydir)
    ncdcid = "%s%s" % (STCONV[station[:2]], station[2:])
    fn = "%s/USC00%s.nc" % (mydir, ncdcid)
    nc = netCDF4.Dataset(fn, 'w')
    nc.set_fill_on()
    nc.US_state = metadata['state']
    nc.ncdc_identifier = ncdcid
    nc.station_name = metadata['name']
    lastyear = datetime.date.today().year + 1
    reclen = int((lastyear-1850) * 365.25) + 1

    nc.createDimension('time', reclen)

    lat = nc.createVariable('lat', np.float)
    lat.standard_name = 'latitude'
    lat.units = 'degree_north'
    lat[0] = metadata['lat']

    lon = nc.createVariable('lon', np.float)
    lon.standard_name = 'longitude'
    lon.units = 'degree_east'
    lon[0] = metadata['lon']

    # Time
    tm = nc.createVariable('time', np.float, ('time',))
    tm.units = "days since 1850-01-01 00:00:00"
    tm.calendar = "gregorian"
    tm[:] = np.arange(reclen)

    # snowfall
    snow = nc.createVariable('prsn', 'f4', ('time',),
                             fill_value=-9999)
    snow.standard_name = 'snowfall_flux'
    snow.units = 'kg m-2 s-1'
    _ = nc.createVariable('prsn_mflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'snowfall_flux mflag'
    _ = nc.createVariable('prsn_qflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'snowfall_flux qflag'
    _ = nc.createVariable('prsn_sflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'snowfall_flux sflag'

    # snow depth
    snowd = nc.createVariable('snowdepth', 'f4', ('time',),
                              fill_value=-9999)
    snowd.long_name = 'Snowfall Depth'
    snowd.units = 'mm'
    _ = nc.createVariable('snowdepth_mflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'Snowfall Depth mflag'
    _ = nc.createVariable('snowdepth_qflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'Snowfall Depth qflag'
    _ = nc.createVariable('snowdepth_sflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'Snowfall Depth sflag'

    # tmax
    tmax = nc.createVariable('tmax', 'f4', ('time',),
                             fill_value=-9999)
    tmax.long_name = 'Temperature Max'
    tmax.units = 'K'
    _ = nc.createVariable('tmax_mflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'Temperature Max mflag'
    _ = nc.createVariable('tmax_qflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'Temperature Max qflag'
    _ = nc.createVariable('tmax_sflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'Temperature Max sflag'

    # tmin
    tmin = nc.createVariable('tmin', 'f4', ('time',),
                             fill_value=-9999)
    tmin.long_name = 'Temperature Min'
    tmin.units = 'K'
    _ = nc.createVariable('tmin_mflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'Temperature Min mflag'
    _ = nc.createVariable('tmin_qflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'Temperature Min qflag'
    _ = nc.createVariable('tmin_sflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'Temperature Min sflag'

    # precip
    precip = nc.createVariable('pr', 'f4', ('time',),
                               fill_value=-9999)
    precip.standard_name = 'precipitation_flux'
    precip.units = 'kg m-2 s-1'
    _ = nc.createVariable('pr_mflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'precipitation_flux mflag'
    _ = nc.createVariable('pr_qflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'precipitation_flux qflag'
    _ = nc.createVariable('pr_sflag', np.uint8, ('time',), fill_value=0)
    _.long_name = 'precipitation_flux sflag'

    return nc


def process(station, metadata):
    ''' Lets process something, stat

    ['TMAX', 'TMIN', 'TOBS', 'PRCP', 'SNOW', 'SNWD', 'EVAP', 'MNPN', 'MXPN',
     'WDMV', 'DAEV', 'MDEV', 'DAWM', 'MDWM', 'WT05', 'SN01', 'SN02', 'SN03',
     'SX01', 'SX02', 'SX03', 'MDPR', 'MDSF', 'SN51', 'SN52', 'SN53', 'SX51',
     'SX52', 'SX53', 'WT01', 'SN31', 'SN32', 'SN33', 'SX31', 'SX32', 'SX33']

    '''
    fp = get_file(station)
    if fp is None:
        return
    nc = create_netcdf(station, metadata)
    if nc is None:
        return
    data = {}
    # reclength = len(nc.dimensions['time'])
    for line in fp:
        m = DATARE.match(line)
        d = m.groupdict()
        if d['element'] not in ['TMAX', 'TMIN', 'PRCP', 'SNOW', 'SNWD']:
            continue
        day = datetime.date(int(d['year']), int(d['month']), 1)
        days = get_days_for_month(day)
        for i in range(1, days+1):
            day = day.replace(day=i)
            # We don't want data in the future!
            if day >= TODAY:
                continue
            if day not in data:
                data[day] = {}
            data[day][d['element']+"mflag"] = d['flag%s' % (i,)][0]
            data[day][d['element']+"qflag"] = d['flag%s' % (i,)][1]
            data[day][d['element']+"sflag"] = d['flag%s' % (i,)][2]
            v = varconv(d['value%s' % (i,)], d['element'])
            if v is not None:
                data[day][d['element']] = v

    table = "alldata_%s" % (station[:2],)
    keys = data.keys()
    keys.sort()

    obs = {}
    cursor.execute("""SELECT day, high, low, precip, snow, snowd from
            """+table+""" where station = %s""", (station,))
    for row in cursor:
        obs[row[0]] = row[1:]
    print 'loadvars'
    pr_mflag = nc.variables['pr_mflag'][:]
    pr_sflag = nc.variables['pr_sflag'][:]
    pr_qflag = nc.variables['pr_qflag'][:]
    pr = nc.variables['pr'][:]

    prsn_mflag = nc.variables['prsn_mflag'][:]
    prsn_qflag = nc.variables['prsn_qflag'][:]
    prsn_sflag = nc.variables['prsn_sflag'][:]
    prsn = nc.variables['prsn'][:]

    snowdepth_mflag = nc.variables['snowdepth_mflag'][:]
    snowdepth_qflag = nc.variables['snowdepth_qflag'][:]
    snowdepth_sflag = nc.variables['snowdepth_sflag'][:]
    snowdepth = nc.variables['snowdepth'][:]

    tmax_mflag = nc.variables['tmax_mflag'][:]
    tmax_qflag = nc.variables['tmax_qflag'][:]
    tmax_sflag = nc.variables['tmax_sflag'][:]
    tmax = nc.variables['tmax'][:]

    tmin_mflag = nc.variables['tmin_mflag'][:]
    tmin_qflag = nc.variables['tmin_qflag'][:]
    tmin_sflag = nc.variables['tmin_sflag'][:]
    tmin = nc.variables['tmin'][:]
    for d in keys:
        row = obs.get(d)
        offset = (d - BASE).days - 1
        pr_mflag[offset] = ord(data[d].get('PRCPmflag', ' '))
        pr_qflag[offset] = ord(data[d].get('PRCPqflag', ' '))
        pr_sflag[offset] = ord(data[d].get('PRCPsflag', ' '))
        if data[d].get('PRCP') is not None:
            pr[offset] = distance(data[d].get('PRCP'),
                                  'IN').value("MM") / 86400.
        prsn_mflag[offset] = ord(data[d].get('SNOWmflag', ' '))
        prsn_qflag[offset] = ord(data[d].get('SNOWqflag', ' '))
        prsn_sflag[offset] = ord(data[d].get('SNOWsflag', ' '))
        if data[d].get('SNOW') is not None:
            prsn[offset] = distance(data[d].get('SNOW'),
                                    'IN').value("MM") / 86400.
        snowdepth_mflag[offset] = ord(data[d].get('SNWDmflag', ' '))
        snowdepth_qflag[offset] = ord(data[d].get('SNWDqflag', ' '))
        snowdepth_sflag[offset] = ord(data[d].get('SNWDsflag', ' '))
        if data[d].get('SNWD') is not None:
            snowdepth[offset] = distance(data[d].get('SNWD'),
                                         'IN').value("MM")
        tmax_mflag[offset] = ord(data[d].get('TMAXmflag', ' '))
        tmax_qflag[offset] = ord(data[d].get('TMAXqflag', ' '))
        tmax_sflag[offset] = ord(data[d].get('TMAXsflag', ' '))
        if data[d].get('TMAX') is not None:
            tmax[offset] = temperature(data[d].get('TMAX'),
                                       'F').value('K')
        tmin_mflag[offset] = ord(data[d].get('TMINmflag', ' '))
        tmin_qflag[offset] = ord(data[d].get('TMINqflag', ' '))
        tmin_sflag[offset] = ord(data[d].get('TMINsflag', ' '))
        if data[d].get('TMIN') is not None:
            tmin[offset] = temperature(data[d].get('TMIN'),
                                       'F').value('K')
        if row is None:
            print 'No data for %s %s' % (station, d)
            cursor.execute("""
                INSERT into %s(station, day, sday,
                year, month) VALUES ('%s', '%s', '%s', %s, %s)
            """ % (table, station, d,
                   "%02i%02i" % (d.month, d.day), d.year,
                   d.month))
            row = [None, None, None, None, None]
        s = ""
        if (data[d].get('TMAX') is not None and
                (row[0] is None or row[0] != data[d]['TMAX'])):
            print 'Update %s High   %5s -> %5s' % (d, row[0],
                                                   data[d]['TMAX'])
            s += "high = %.0f," % (data[d]['TMAX'],)

        if (data[d].get('TMIN') is not None and
                (row[1] is None or row[1] != data[d]['TMIN'])):
            print 'Update %s Low    %5s -> %5s' % (d, row[1],
                                                   data[d]['TMIN'])
            s += "low = %.0f," % (data[d]['TMIN'],)

        if (data[d].get('PRCP') is not None and
                (row[2] is None or row[2] != data[d]['PRCP'])):
            print 'Update %s Precip %5s -> %5s' % (d, row[2],
                                                   data[d]['PRCP'])
            s += "precip = %.2f," % (data[d]['PRCP'],)

        if (data[d].get('SNOW') is not None and
                (row[3] is None or row[3] != data[d]['SNOW'])):
            print 'Update %s Snow   %5s -> %5s' % (d, row[3],
                                                   data[d]['SNOW'])
            s += "snow = %.1f," % (data[d]['SNOW'],)

        if (data[d].get('SNWD') is not None and
                (row[4] is None or row[4] != data[d]['SNWD'])):
            print 'Update %s Snowd  %5s -> %5s' % (d, row[4],
                                                   data[d]['SNWD'])
            s += "snowd = %.1f," % (data[d]['SNWD'],)

        if s != "":
            sql = """
            UPDATE %s SET %s WHERE day = '%s' and
            station = '%s'
            """ % (table, s[:-1], d, station)
            cursor.execute(sql)

    # print 'Write pr netcdf'
    nc.variables['pr'][:] = pr
    # print 'Write pr_mflag netcdf'
    nc.variables['pr_mflag'][:] = pr_mflag
    # print 'Write pr_qflag netcdf'
    nc.variables['pr_qflag'][:] = pr_qflag
    # print 'Write pr_sflag netcdf'
    nc.variables['pr_sflag'][:] = pr_sflag

    # print 'Write prsn netcdf'
    nc.variables['prsn'][:] = prsn
    nc.variables['prsn_mflag'][:] = prsn_mflag
    nc.variables['prsn_qflag'][:] = prsn_qflag
    nc.variables['prsn_sflag'][:] = prsn_sflag

    # print 'Write snowdepth netcdf'
    nc.variables['snowdepth'][:] = snowdepth
    nc.variables['snowdepth_mflag'][:] = snowdepth_mflag
    nc.variables['snowdepth_qflag'][:] = snowdepth_qflag
    nc.variables['snowdepth_sflag'][:] = snowdepth_sflag

    # print 'Write tmax netcdf'
    nc.variables['tmax'][:] = tmax
    nc.variables['tmax_mflag'][:] = tmax_mflag
    nc.variables['tmax_qflag'][:] = tmax_qflag
    nc.variables['tmax_sflag'][:] = tmax_sflag

    # print 'Write tmin netcdf'
    nc.variables['tmin'][:] = tmin
    nc.variables['tmin_mflag'][:] = tmin_mflag
    nc.variables['tmin_qflag'][:] = tmin_qflag
    nc.variables['tmin_sflag'][:] = tmin_sflag
    # print 'Done writing'
    nc.close()
    # print 'done'


def main():
    """ go main go """
    station = sys.argv[1]
    if len(station) == 2:
        # we have a state!
        nt = NetworkTable("%sCLIMATE" % (station,))
        for sid in nt.sts.keys():
            if sid[2:] == '0000' or sid[2] == 'C':
                continue
            process(sid, nt.sts[sid])
    elif station == 'ALL':
        for state in STCONV.keys():
            nt = NetworkTable("%sCLIMATE" % (state,))
            for sid in nt.sts.keys():
                if sid[2:] == '0000' or sid[2] == 'C':
                    continue
                process(sid, nt.sts[sid])
    else:
        station = sys.argv[1]
        nt = NetworkTable("%sCLIMATE" % (station[:2],))
        process(sys.argv[1], nt.sts[station])


if __name__ == '__main__':
    main()
    cursor.close()
    COOP.commit()
    COOP.close()
