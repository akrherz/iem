"""
 Ingest ISU SOILM data!

 Run from RUN_10_AFTER.sh
"""
# stdlib
import os
import pytz
import datetime
import subprocess
import tempfile

# Third party
import numpy as np
from pyiem.observation import Observation
from pyiem.datatypes import temperature, humidity, distance
import pyiem.meteorology as met
import psycopg2
ISUAG = psycopg2.connect(database='isuag',  host='iemdb')
icursor = ISUAG.cursor()

ACCESS = psycopg2.connect(database='iem', host='iemdb')
accesstxn = ACCESS.cursor()

REPROCESS_SOLAR = False
VARCONV = {
           'vwc06_avg': 'vwc_06_avg',
           'vwc12_avg': 'vwc_12_avg',
           'vwc24_avg': 'vwc_24_avg',
           'vwc50_avg': 'vwc_50_avg',
           'calcvwc06_avg': 'vwc_06_avg',
           'calcvwc12_avg': 'vwc_12_avg',
           'calcvwc24_avg': 'vwc_24_avg',
           'calcvwc50_avg': 'vwc_50_avg',
           }

BASE = '/mnt/home/loggernet'
STATIONS = {'CAMI4': 'Calumet',
            'BOOI4': 'AEAFarm',
            'WMNI4': 'Wellman',
            'SBEI4': 'Sibley',
            'NASI4': 'Nashua',
            'OKLI4': 'Lewis',
            'WTPI4': 'WestPoint',
            'DONI4': 'Doon',
            'KNAI4': 'Kanawha',
            'GREI4': 'Greenfield',
            'NWLI4': 'Newell',
            'AEEI4': 'Ames',
            'CNAI4': 'Castana',
            'CHAI4': 'Chariton',
            'CRFI4': 'Crawfordsville',
            'FRUI4': 'Muscatine',
            'CIRI4': 'CedarRapids',
            }


def make_time(s):
    """Convert a time in the file to a datetime"""
    ts = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    ts = ts.replace(tzinfo=pytz.FixedOffset(-360))
    return ts


def m15_process(nwsli, maxts):
    """ Process the 15minute file """
    fn = "%s/%s_Min15SI.dat" % (BASE, STATIONS[nwsli])
    if not os.path.isfile(fn):
        return
    lines = open(fn).readlines()
    if len(lines) < 5:
        return
    # Read header....
    headers = []
    for col in lines[1].strip().replace('"', '').split(","):
        headers.append(VARCONV.get(col.lower(), col.lower()))
    # Read data
    processed = 0
    for i in range(len(lines)-1, 3, -1):
        tokens = lines[i].strip().replace('"', '').split(",")
        if len(tokens) != len(headers):
            continue
        valid = make_time(tokens[headers.index('timestamp')])
        if valid <= maxts:
            break
        gust_valid = make_time(tokens[headers.index('ws_mph_tmx')])
        # print valid, tokens[ headers.index('timestamp')]
        # We are ready for dbinserting, we duplicate the data for the _qc
        # column
        dbcols = ("station,valid,%s,%s"
                  ) % (",".join(headers[2:]),
                       ",".join(["%s_qc" % (h,) for h in headers[2:]]))
        dbvals = "'%s','%s-06'," % (nwsli, valid.strftime("%Y-%m-%d %H:%M:%S"))
        for v in tokens[2:]:
            dbvals += "%s," % (formatter(v),)
        for v in tokens[2:]:
            dbvals += "%s," % (formatter(v),)
        sql = "INSERT into sm_15minute (%s) values (%s)" % (dbcols,
                                                            dbvals[:-1])
        icursor.execute(sql)

        # Update IEMAccess
        # print nwsli, valid
        ob = Observation(nwsli, 'ISUSM',
                         valid.astimezone(pytz.timezone("America/Chicago")))
        tmpc = temperature(float(tokens[headers.index('tair_c_avg')]), 'C')
        if tmpc.value('F') > -50 and tmpc.value('F') < 140:
            ob.data['tmpf'] = tmpc.value('F')
            relh = humidity(float(tokens[headers.index('rh')]), '%')
            ob.data['relh'] = relh.value('%')
            ob.data['dwpf'] = met.dewpoint(tmpc, relh).value('F')
        ob.data['srad'] = tokens[headers.index('slrkw_avg')]
        ob.data['phour'] = round(
            distance(
                     float(tokens[headers.index('rain_mm_tot')]),
                     'MM').value('IN'), 2)
        ob.data['sknt'] = float(tokens[headers.index('ws_mps_s_wvt')]) * 1.94
        ob.data['gust'] = float(tokens[headers.index('ws_mph_max')]) / 1.15
        ob.data['max_gust_ts'] = "%s-06" % (
            gust_valid.strftime("%Y-%m-%d %H:%M:%S"),)
        ob.data['drct'] = float(tokens[headers.index('winddir_d1_wvt')])
        ob.data['c1tmpf'] = temperature(
                float(tokens[headers.index('tsoil_c_avg')]), 'C').value('F')
        ob.data['c2tmpf'] = temperature(
                float(tokens[headers.index('t12_c_avg')]), 'C').value('F')
        ob.data['c3tmpf'] = temperature(
                float(tokens[headers.index('t24_c_avg')]), 'C').value('F')
        ob.data['c4tmpf'] = temperature(
                float(tokens[headers.index('t50_c_avg')]), 'C').value('F')
        ob.data['c2smv'] = float(tokens[headers.index('vwc_12_avg')]) * 100.0
        ob.data['c3smv'] = float(tokens[headers.index('vwc_24_avg')]) * 100.0
        ob.data['c4smv'] = float(tokens[headers.index('vwc_50_avg')]) * 100.0
        ob.save(accesstxn, force_current_log=True)
        # print 'soilm_ingest.py station: %s ts: %s hrly updated no data?' % (
        #                                        nwsli, valid)
        processed += 1
    return processed


def hourly_process(nwsli, maxts):
    """ Process the hourly file """
    # print '-------------- HOURLY PROCESS ---------------'
    fn = "%s/%s_HrlySI.dat" % (BASE, STATIONS[nwsli])
    if not os.path.isfile(fn):
        return
    lines = open(fn).readlines()
    if len(lines) < 5:
        return
    # Read header....
    headers = []
    for col in lines[1].strip().replace('"', '').split(","):
        headers.append(VARCONV.get(col.lower(), col.lower()))
    # Read data
    processed = 0
    for i in range(len(lines)-1, 3, -1):
        tokens = lines[i].strip().replace('"', '').split(",")
        if len(tokens) != len(headers):
            continue
        valid = make_time(tokens[headers.index('timestamp')])
        if valid <= maxts:
            break
        gust_valid = make_time(tokens[headers.index('ws_mph_tmx')])
        # print valid, tokens[ headers.index('timestamp')]
        # We are ready for dbinserting, we duplicate the data for the _qc
        # column
        dbcols = ("station,valid,%s,%s"
                  ) % (",".join(headers[2:]),
                       ",".join(["%s_qc" % (h,) for h in headers[2:]]))
        dbvals = "'%s','%s-06'," % (nwsli, valid.strftime("%Y-%m-%d %H:%M:%S"))
        for v in tokens[2:]:
            dbvals += "%s," % (formatter(v),)
        for v in tokens[2:]:
            dbvals += "%s," % (formatter(v),)
        sql = "INSERT into sm_hourly (%s) values (%s)" % (dbcols, dbvals[:-1])
        icursor.execute(sql)

        # Update IEMAccess
        # print nwsli, valid
        ob = Observation(nwsli, 'ISUSM',
                         valid.astimezone(pytz.timezone("America/Chicago")))
        tmpc = temperature(float(tokens[headers.index('tair_c_avg')]), 'C')
        if tmpc.value('F') > -50 and tmpc.value('F') < 140:
            ob.data['tmpf'] = tmpc.value('F')
            relh = humidity(float(tokens[headers.index('rh')]), '%')
            ob.data['relh'] = relh.value('%')
            ob.data['dwpf'] = met.dewpoint(tmpc, relh).value('F')
        ob.data['srad'] = tokens[headers.index('slrkw_avg')]
        ob.data['phour'] = round(
            distance(
                     float(tokens[headers.index('rain_mm_tot')]),
                     'MM').value('IN'), 2)
        ob.data['sknt'] = float(tokens[headers.index('ws_mps_s_wvt')]) * 1.94
        ob.data['gust'] = float(tokens[headers.index('ws_mph_max')]) / 1.15
        ob.data['max_gust_ts'] = "%s-06" % (
            gust_valid.strftime("%Y-%m-%d %H:%M:%S"),)
        ob.data['drct'] = float(tokens[headers.index('winddir_d1_wvt')])
        ob.data['c1tmpf'] = temperature(
                float(tokens[headers.index('tsoil_c_avg')]), 'C').value('F')
        ob.data['c2tmpf'] = temperature(
                float(tokens[headers.index('t12_c_avg')]), 'C').value('F')
        ob.data['c3tmpf'] = temperature(
                float(tokens[headers.index('t24_c_avg')]), 'C').value('F')
        ob.data['c4tmpf'] = temperature(
                float(tokens[headers.index('t50_c_avg')]), 'C').value('F')
        ob.data['c2smv'] = float(tokens[headers.index('vwc_12_avg')]) * 100.0
        ob.data['c3smv'] = float(tokens[headers.index('vwc_24_avg')]) * 100.0
        ob.data['c4smv'] = float(tokens[headers.index('vwc_50_avg')]) * 100.0
        ob.save(accesstxn)
        # print 'soilm_ingest.py station: %s ts: %s hrly updated no data?' % (
        #                                        nwsli, valid)
        processed += 1
    return processed


def formatter(v):
    """ Something to format things nicely for SQL"""
    if v.find("NAN") > -1:
        return 'Null'
    if v.find(" ") > -1:  # Timestamp
        return "'%s-06'" % (v,)
    return v


def daily_process(nwsli, maxts):
    """ Process the daily file """
    # print '-------------- DAILY PROCESS ----------------'
    fn = "%s/%s_DailySI.dat" % (BASE, STATIONS[nwsli])
    if not os.path.isfile(fn):
        return 0
    lines = open(fn).readlines()
    if len(lines) < 5:
        return 0
    # Read header....
    headers = []
    for col in lines[1].strip().replace('"', '').split(","):
        headers.append(VARCONV.get(col.lower(), col.lower()))
    # Read data
    processed = 0
    for i in range(len(lines)-1, 3, -1):
        tokens = lines[i].strip().replace('"', '').split(",")
        if len(tokens) != len(headers):
            continue
        valid = datetime.datetime.strptime(
            tokens[headers.index('timestamp')][:10], '%Y-%m-%d')
        valid = valid.date() - datetime.timedelta(days=1)
        if valid <= maxts:
            break
        # if valid == maxts:  # Reprocess
        #    icursor.execute("""DELETE from sm_daily WHERE valid = '%s' and
        #    station = '%s' """ % (valid.strftime("%Y-%m-%d"), nwsli))
        # We are ready for dbinserting!
        dbcols = ("station,valid,%s,%s"
                  ) % (",".join(headers[2:]),
                       ",".join(["%s_qc" % (h,) for h in headers[2:]]))
        dbvals = "'%s','%s-06'," % (nwsli, valid.strftime("%Y-%m-%d %H:%M:%S"))
        for v in tokens[2:]:
            dbvals += "%s," % (formatter(v),)
        for v in tokens[2:]:
            dbvals += "%s," % (formatter(v),)
        sql = "INSERT into sm_daily (%s) values (%s)" % (dbcols, dbvals[:-1])
        icursor.execute(sql)

        # Need a timezone
        valid = datetime.datetime(valid.year, valid.month, valid.day, 12, 0)
        valid = valid.replace(tzinfo=pytz.timezone("America/Chicago"))
        ob = Observation(nwsli, 'ISUSM', valid)
        ob.data['max_tmpf'] = temperature(
                    float(tokens[headers.index('tair_c_max')]), 'C').value('F')
        ob.data['min_tmpf'] = temperature(
                    float(tokens[headers.index('tair_c_min')]), 'C').value('F')
        ob.data['pday'] = round(distance(
            float(tokens[headers.index('rain_mm_tot')]), 'MM').value('IN'), 2)
        ob.data['et_inch'] = distance(
            float(tokens[headers.index('dailyet')]), 'MM').value('IN')
        ob.data['srad_mj'] = float(tokens[headers.index('slrmj_tot')])
        if ob.data['srad_mj'] == 0 or np.isnan(ob.data['srad_mj']):
            print(("soilm_ingest.py station: %s ts: %s has 0 solar"
                   ) % (nwsli, valid.strftime("%Y-%m-%d")))
            global REPROCESS_SOLAR
            REPROCESS_SOLAR = True
        ob.data['max_sknt'] = float(tokens[headers.index('ws_mps_max')]) * 1.94
        ob.save(accesstxn)
        # print 'soilm_ingest.py station: %s ts: %s daily updated no data?' % (
        #                                nwsli, valid.strftime("%Y-%m-%d"))
        processed += 1
    return processed


def update_pday():
    ''' Compute today's precip from the current_log archive of data '''
    accesstxn.execute("""
    SELECT s.iemid, sum(case when phour > 0 then phour else 0 end) from
    current_log s JOIN stations t on (t.iemid = s.iemid)
    WHERE t.network = 'ISUSM' and valid > 'TODAY' GROUP by s.iemid
    """)
    data = {}
    for row in accesstxn:
        data[row[0]] = row[1]

    for iemid in data.keys():
        accesstxn.execute("""UPDATE summary SET pday = %s
        WHERE iemid = %s and day = 'TODAY'""", (data[iemid], iemid))


def get_max_timestamps(nwsli):
    """ Fetch out our max values """
    data = {'hourly': datetime.datetime(2012, 1, 1,
                                        tzinfo=pytz.FixedOffset(-360)),
            '15minute': datetime.datetime(2012, 1, 1,
                                          tzinfo=pytz.FixedOffset(-360)),
            'daily': datetime.date(2012, 1, 1)}
    icursor.execute("""SELECT max(valid) from sm_daily
        WHERE station = '%s'""" % (nwsli, ))
    row = icursor.fetchone()
    if row[0] is not None:
        data['daily'] = row[0]

    icursor.execute("""
        SELECT max(valid) from sm_hourly
        WHERE station = '%s'
        """ % (nwsli, ))
    row = icursor.fetchone()
    if row[0] is not None:
        data['hourly'] = row[0]

    icursor.execute("""
        SELECT max(valid) from sm_15minute
        WHERE station = '%s'
        """ % (nwsli, ))
    row = icursor.fetchone()
    if row[0] is not None:
        data['15minute'] = row[0]
    return data


def dump_raw_to_ldm(nwsli, dyprocessed, hrprocessed):
    """ Send the raw datafile to LDM """
    fn = "%s/%s_DailySI.dat" % (BASE, STATIONS[nwsli])
    if not os.path.isfile(fn):
        return
    lines = open(fn).readlines()
    if len(lines) < 5:
        return

    tmpfn = tempfile.mktemp()
    tmpfp = open(tmpfn, 'w')
    tmpfp.write(lines[0])
    tmpfp.write(lines[1])
    tmpfp.write(lines[2])
    tmpfp.write(lines[3])
    for linenum in range(0 - dyprocessed, 0):
        tmpfp.write(lines[linenum])
    tmpfp.close()
    cmd = ("/home/ldm/bin/pqinsert -p "
           "'data c %s csv/isusm/%s_daily.txt bogus txt' %s"
           ) % (datetime.datetime.utcnow().strftime("%Y%m%d%H%M"), nwsli,
                tmpfn)
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    p.stdout.read()
    os.remove(tmpfn)

    """ Send the raw datafile to LDM """
    fn = "%s/%s_HrlySI.dat" % (BASE, STATIONS[nwsli])
    if not os.path.isfile(fn):
        return
    lines = open(fn).readlines()
    if len(lines) < 5:
        return

    tmpfn = tempfile.mktemp()
    tmpfp = open(tmpfn, 'w')
    tmpfp.write(lines[0])
    tmpfp.write(lines[1])
    tmpfp.write(lines[2])
    tmpfp.write(lines[3])
    for linenum in range(0 - hrprocessed, 0):
        tmpfp.write(lines[linenum])
    tmpfp.close()
    cmd = ("/home/ldm/bin/pqinsert -p "
           "'data c %s csv/isusm/%s_hourly.txt bogus txt' %s"
           ) % (datetime.datetime.utcnow().strftime("%Y%m%d%H%M"), nwsli,
                tmpfn)
    proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    proc.stdout.read()
    os.remove(tmpfn)


def main():
    """ Go main Go """
    for nwsli in STATIONS.keys():
        maxobs = get_max_timestamps(nwsli)
        if nwsli != 'BOOI4':
            _ = m15_process(nwsli, maxobs['15minute'])
        hrprocessed = hourly_process(nwsli, maxobs['hourly'])
        dyprocessed = daily_process(nwsli, maxobs['daily'])
        if hrprocessed > 0:
            dump_raw_to_ldm(nwsli, dyprocessed, hrprocessed)
        # else:
        #    print 'No LDM data sent for %s' % (nwsli,)
    update_pday()
    icursor.close()
    ISUAG.commit()
    ISUAG.close()

    accesstxn.close()
    ACCESS.commit()
    ACCESS.close()

    if REPROCESS_SOLAR:
        print("Calling fix_solar.py")
        os.chdir("../isuag")
        subprocess.call("python fix_solar.py", shell=True)

if __name__ == '__main__':
    main()
