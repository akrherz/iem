"""
 Ingest ISU SOILM data!

 Run from RUN_10_AFTER.sh
"""
# stdlib
from __future__ import print_function
import datetime
import os
import sys
import subprocess
import tempfile
import io

# Third party
import requests
import pytz
import numpy as np
import pandas as pd
from pyiem.observation import Observation
from pyiem.datatypes import temperature, humidity, distance, speed
import pyiem.meteorology as met
from pyiem.util import get_dbconn

ISUAG = get_dbconn('isuag')

ACCESS = get_dbconn('iem')

EVENTS = {'reprocess_solar': False, 'days': [], 'reprocess_temps': False}
VARCONV = {'timestamp': 'valid',
           'vwc06_avg': 'vwc_06_avg',
           "vwc_avg6in": 'vwc_06_avg',
           'vwc12_avg': 'vwc_12_avg',
           "vwc_avg12in": 'vwc_12_avg',
           'vwc24_avg': 'vwc_24_avg',
           "vwc_avg24in": 'vwc_24_avg',
           'vwc50_avg': 'vwc_50_avg',
           'calcvwc06_avg': 'calc_vwc_06_avg',
           'calcvwc12_avg': 'calc_vwc_12_avg',
           'calcvwc24_avg': 'calc_vwc_24_avg',
           'calcvwc50_avg': 'calc_vwc_50_avg',
           "outofrange06": "P06OutOfRange",
           "outofrange12": "P12OutOfRange",
           "outofrange24": "P24OutOfRange",
           "outofrange50": "P50OutOfRange",
           "ws_ms_s_wvt": "ws_mps_s_wvt",
           "ec6in": "ec06",
           "ec12in": "ec12",
           "ec_24in": "ec24",
           "ec24in": "ec24",
           "temp_avg6in": "t06_c_avg",
           "temp_avg12in": "t12_c_avg",
           "temp_avg24in": "t24_c_avg",
           "bp_mmhg_avg": "bpres_avg",
           }

TSOIL_COLS = ['tsoil_c_avg', 't06_c_avg', 't12_c_avg', 't24_c_avg',
              't50_c_avg']
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
            'MCSI4': 'Marcus',
            'AMFI4': 'AmesFinch',
            # Temporary?
            # 'REFI4': 'Adel',
            # Vineyward
            'AHTI4': 'AmesHort',
            'OSTI4': 'TasselRidge',
            'BNKI4': 'Bankston',
            'CSII4': 'Inwood',
            'GVNI4': 'Glenwood',
            'TPOI4': 'Masonville',
            }


def qcval(df, colname, floor, ceiling):
    """Make sure the value falls within some bounds"""
    df.loc[df[colname] < floor, colname] = floor
    df.loc[df[colname] > ceiling, colname] = ceiling
    return np.where(np.logical_or(df[colname] == floor,
                                  df[colname] == ceiling),
                    'B', None)


def qcval2(df, colname, floor, ceiling):
    """Make sure the value falls within some bounds, Null if not"""
    df.loc[df[colname] < floor, colname] = np.nan
    df.loc[df[colname] > ceiling, colname] = np.nan
    return np.where(pd.isnull(df[colname]), 'B', None)


def make_time(string):
    """Convert a time in the file to a datetime"""
    tstamp = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
    tstamp = tstamp.replace(tzinfo=pytz.FixedOffset(-360))
    return tstamp


def common_df_logic(filename, maxts, nwsli, tablename):
    """Our commonality to reading"""
    if not os.path.isfile(filename):
        return

    df = pd.read_csv(filename, skiprows=[0, 2, 3], na_values=['NAN', ])
    # convert all columns to lowercase
    df.columns = map(str.lower, df.columns)
    # rename columns to rectify differences
    df.rename(columns=VARCONV, inplace=True)
    df['valid'] = df['valid'].apply(make_time)
    if tablename == 'sm_daily':
        # Rework the valid column into the appropriate date
        df['valid'] = df['valid'].dt.date - datetime.timedelta(days=1)
    df = df[df['valid'] > maxts].copy()
    if df.empty:
        return

    df.drop('record', axis=1, inplace=True)
    # Create _qc and _f columns
    for colname in df.columns:
        if colname == 'valid':
            continue
        df['%s_qc' % (colname, )] = df[colname]
        if colname.startswith('calc_vwc'):
            df['%s_f' % (colname, )] = qcval(df, '%s_qc' % (colname, ),
                                             0.01, 0.7)
        elif colname in TSOIL_COLS:
            df['%s_f' % (colname, )] = qcval2(df, '%s_qc' % (colname, ),
                                              -20., 37.)
        else:
            df['%s_f' % (colname, )] = None

    df['station'] = nwsli
    if 'ws_mph_tmx' in df.columns:
        df['ws_mph_tmx'] = df['ws_mph_tmx'].apply(make_time)
    output = io.StringIO()
    df.to_csv(output, sep="\t", header=False, index=False)
    output.seek(0)
    icursor = ISUAG.cursor()
    icursor.copy_from(output, tablename,
                      columns=df.columns, null="")
    icursor.close()
    ISUAG.commit()
    return df


def m15_process(nwsli, maxts):
    """ Process the 15minute file """
    acursor = ACCESS.cursor()
    fn = "%s/%s_Min15SI.dat" % (BASE, STATIONS[nwsli])
    df = common_df_logic(fn, maxts, nwsli, "sm_15minute")
    if df is None:
        return 0

    # Update IEMAccess
    processed = 0
    for _i, row in df.iterrows():
        ob = Observation(nwsli, 'ISUSM', row['valid'])
        tmpc = temperature(row['tair_c_avg_qc'], 'C')
        if tmpc.value('F') > -50 and tmpc.value('F') < 140:
            ob.data['tmpf'] = tmpc.value('F')
            relh = humidity(row['rh_qc'], '%')
            ob.data['relh'] = relh.value('%')
            ob.data['dwpf'] = met.dewpoint(tmpc, relh).value('F')
        ob.data['srad'] = row['slrkw_avg_qc']
        ob.data['pcounter'] = round(
            distance(row['rain_mm_tot_qc'], 'MM').value('IN'), 2)
        ob.data['sknt'] = speed(row['ws_mps_s_wvt_qc'], 'MPS').value('KT')
        ob.data['gust'] = speed(row['ws_mph_max_qc'], 'MPH').value('KT')
        ob.data['max_gust_ts'] = row['ws_mph_tmx']
        ob.data['drct'] = row['winddir_d1_wvt_qc']
        if 'tsoil_c_avg' in df.columns:
            ob.data['c1tmpf'] = temperature(row['tsoil_c_avg_qc'],
                                            'C').value('F')
        ob.data['c2tmpf'] = temperature(row['t12_c_avg_qc'], 'C').value('F')
        ob.data['c3tmpf'] = temperature(row['t24_c_avg_qc'], 'C').value('F')
        if 't50_c_avg' in df.columns:
            ob.data['c4tmpf'] = temperature(row['t50_c_avg_qc'],
                                            'C').value('F')
        if 'calc_vwc_12_avg' in df.columns:
            ob.data['c2smv'] = row['calc_vwc_12_avg_qc'] * 100.0
        if 'calc_vwc_24_avg' in df.columns:
            ob.data['c3smv'] = row['calc_vwc_24_avg_qc'] * 100.0
        if 'calc_vwc_50_avg' in df.columns:
            ob.data['c4smv'] = row['calc_vwc_50_avg_qc'] * 100.0
        ob.save(acursor, force_current_log=True)
        # print 'soilm_ingest.py station: %s ts: %s hrly updated no data?' % (
        #                                        nwsli, valid)
        processed += 1
    acursor.close()
    ACCESS.commit()
    return processed


def hourly_process(nwsli, maxts):
    """ Process the hourly file """
    # print '-------------- HOURLY PROCESS ---------------'
    acursor = ACCESS.cursor()
    fn = "%s/%s_HrlySI.dat" % (BASE, STATIONS[nwsli])
    df = common_df_logic(fn, maxts, nwsli, "sm_hourly")
    if df is None:
        return 0
    processed = 0
    for _i, row in df.iterrows():
        # Update IEMAccess
        # print nwsli, valid
        ob = Observation(nwsli, 'ISUSM', row['valid'])
        tmpc = temperature(row['tair_c_avg_qc'], 'C')
        if tmpc.value('F') > -50 and tmpc.value('F') < 140:
            ob.data['tmpf'] = tmpc.value('F')
            relh = humidity(row['rh_qc'], '%')
            ob.data['relh'] = relh.value('%')
            ob.data['dwpf'] = met.dewpoint(tmpc, relh).value('F')
        ob.data['srad'] = row['slrkw_avg_qc']
        ob.data['phour'] = round(distance(row['rain_mm_tot_qc'],
                                          'MM').value('IN'), 2)
        ob.data['sknt'] = speed(row['ws_mps_s_wvt_qc'], 'MPS').value("KT")
        if 'ws_mph_max' in df.columns:
            ob.data['gust'] = speed(row['ws_mph_max_qc'], 'MPH').value('KT')
            ob.data['max_gust_ts'] = row['ws_mph_tmx']
        ob.data['drct'] = row['winddir_d1_wvt_qc']
        if 'tsoil_c_avg' in df.columns:
            ob.data['c1tmpf'] = temperature(row['tsoil_c_avg_qc'],
                                            'C').value('F')
        ob.data['c2tmpf'] = temperature(row['t12_c_avg_qc'], 'C').value('F')
        ob.data['c3tmpf'] = temperature(row['t24_c_avg_qc'], 'C').value('F')
        if 't50_c_avg' in df.columns:
            ob.data['c4tmpf'] = temperature(row['t50_c_avg_qc'],
                                            'C').value('F')
        if 'calc_vwc_12_avg' in df.columns:
            ob.data['c2smv'] = row['calc_vwc_12_avg_qc'] * 100.0
        if 'calc_vwc_24_avg' in df.columns:
            ob.data['c3smv'] = row['calc_vwc_24_avg_qc'] * 100.0
        if 'calc_vwc_50_avg' in df.columns:
            ob.data['c4smv'] = row['calc_vwc_50_avg_qc'] * 100.0
        ob.save(acursor)
        # print 'soilm_ingest.py station: %s ts: %s hrly updated no data?' % (
        #                                        nwsli, valid)
        processed += 1
    acursor.close()
    ACCESS.commit()
    return processed


def daily_process(nwsli, maxts):
    """ Process the daily file """
    acursor = ACCESS.cursor()
    # print '-------------- DAILY PROCESS ----------------'
    fn = "%s/%s_DailySI.dat" % (BASE, STATIONS[nwsli])
    df = common_df_logic(fn, maxts, nwsli, "sm_daily")
    if df is None:
        return 0

    processed = 0
    for _i, row in df.iterrows():
        # Need a timezone
        valid = datetime.datetime(row['valid'].year, row['valid'].month,
                                  row['valid'].day, 12, 0)
        valid = valid.replace(tzinfo=pytz.timezone("America/Chicago"))
        ob = Observation(nwsli, 'ISUSM', valid)
        ob.data['max_tmpf'] = temperature(row['tair_c_max_qc'], 'C').value('F')
        ob.data['min_tmpf'] = temperature(row['tair_c_min_qc'], 'C').value('F')
        ob.data['pday'] = round(distance(row['rain_mm_tot_qc'],
                                         'MM').value('IN'), 2)
        if valid not in EVENTS['days']:
            EVENTS['days'].append(valid)
        ob.data['et_inch'] = distance(row['dailyet_qc'], 'MM').value('IN')
        ob.data['srad_mj'] = row['slrmj_tot_qc']
        # Someday check if this is apples to apples here
        ob.data['vector_avg_drct'] = row['winddir_d1_wvt_qc']
        if ob.data['max_tmpf'] is None:
            EVENTS['reprocess_temps'] = True
        if ob.data['srad_mj'] == 0 or np.isnan(ob.data['srad_mj']):
            print(("soilm_ingest.py station: %s ts: %s has 0 solar"
                   ) % (nwsli, valid.strftime("%Y-%m-%d")))
            EVENTS['reprocess_solar'] = True
        if 'ws_mps_max' in df.columns:
            ob.data['max_sknt'] = speed(row['ws_mps_max_qc'],
                                        'MPS').value('KT')
        ob.data['avg_sknt'] = speed(row['ws_mps_s_wvt_qc'], 'MPS').value('KT')
        ob.save(acursor)

        processed += 1
    acursor.close()
    ACCESS.commit()
    return processed


def update_pday():
    ''' Compute today's precip from the current_log archive of data '''
    acursor = ACCESS.cursor()
    acursor.execute("""
    SELECT s.iemid, sum(case when phour > 0 then phour else 0 end) from
    current_log s JOIN stations t on (t.iemid = s.iemid)
    WHERE t.network = 'ISUSM' and valid > 'TODAY' GROUP by s.iemid
    """)
    data = {}
    for row in acursor:
        data[row[0]] = row[1]

    for iemid in data:
        acursor.execute("""UPDATE summary SET pday = %s
        WHERE iemid = %s and day = 'TODAY'""", (data[iemid], iemid))
    acursor.close()
    ACCESS.commit()


def get_max_timestamps(nwsli):
    """ Fetch out our max values """
    icursor = ISUAG.cursor()
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
    filename = "%s/%s_DailySI.dat" % (BASE, STATIONS[nwsli])
    if not os.path.isfile(filename):
        return
    lines = open(filename).readlines()
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
    proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    proc.stdout.read()
    os.remove(tmpfn)

    # Send the raw datafile to LDM
    filename = "%s/%s_HrlySI.dat" % (BASE, STATIONS[nwsli])
    if not os.path.isfile(filename):
        return
    lines = open(filename).readlines()
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


def dump_madis_csv():
    """Inject the current MADIS NMP csv into LDM"""
    uri = "http://iem.local/agclimate/isusm.csv"
    req = requests.get(uri)
    output = open('/tmp/isusm.csv', 'wb')
    output.write(req.content)
    output.close()
    subprocess.call("/home/ldm/bin/pqinsert -p 'isusm.csv' /tmp/isusm.csv",
                    shell=True)


def main(argv):
    """ Go main Go """
    stations = STATIONS if len(argv) == 1 else [argv[1], ]
    for nwsli in stations:
        maxobs = get_max_timestamps(nwsli)
        m15processed = m15_process(nwsli, maxobs['15minute'])
        hrprocessed = hourly_process(nwsli, maxobs['hourly'])
        dyprocessed = daily_process(nwsli, maxobs['daily'])
        if hrprocessed > 0:
            dump_raw_to_ldm(nwsli, dyprocessed, hrprocessed)
        if len(argv) > 1:
            print("%s 15min:%s hr:%s daily:%s" % (nwsli, m15processed,
                                                  hrprocessed, dyprocessed))
    update_pday()

    if EVENTS['reprocess_solar']:
        print("Calling fix_solar.py")
        subprocess.call("python ../isuag/fix_solar.py", shell=True)
    if EVENTS['reprocess_temps']:
        print("Calling fix_temps.py")
        subprocess.call("python ../isuag/fix_temps.py", shell=True)
    for day in EVENTS['days']:
        subprocess.call(("python ../isuag/fix_precip.py %s %s %s"
                         ) % (day.year, day.month, day.day), shell=True)
        subprocess.call(("python ../isuag/fix_solar.py %s %s %s"
                         ) % (day.year, day.month, day.day), shell=True)

    dump_madis_csv()


def test_make_tstamp():
    """Do we do the right thing with timestamps"""
    res = make_time("2017-08-31 19:00:00")
    assert res.strftime("%H") == "19"


if __name__ == '__main__':
    main(sys.argv)
