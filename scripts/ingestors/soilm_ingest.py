"""
 Ingest ISU SOILM data!
 
 Run from RUN_10_AFTER.sh 
 
 DailySI
 "TIMESTAMP",
 "RECORD",
 "TAir_C_Avg",
 "TAir_C_Max",
 "TAir_C_TMx",
 "TAir_C_Min",
 "TAir_C_TMn",
 "SlrMJ_Tot",
 "Rain_mm_Tot",
 "WS_mps_S_WVT",
 "WindDir_D1_WVT",
 "WindDir_SD1_WVT",
 "WS_mps_Max",
 "WS_mps_TMx",
 "DailyET",
 "TSoil_C_Avg",
 "VWC_12_Avg",
 "VWC_24_Avg",
 "VWC_50_Avg",
 "EC12",
 "EC24",
 "EC50",
 "T12_C_Avg",
 "T24_C_Avg",
 "T50_C_Avg",
 "PA",
 "PA_2",
 "PA_3"
 
 HrlySI
 "TIMESTAMP",
 "RECORD",
 "TAir_C_Avg",
 "RH",
 "SlrkW_Avg",
 "SlrMJ_Tot",
 "Rain_mm_Tot",
 "WS_mps_S_WVT",
 "WindDir_D1_WVT",
 "WindDir_SD1_WVT",
 "ETAlfalfa",
 "SolarRadCalc",
 "TSoil_C_Avg",
 "VWC_12_Avg",
 "VWC_24_Avg",
 "VWC_50_Avg",
 "EC12",
 "EC24",
 "EC50",
 "T12_C_Avg",
 "T24_C_Avg",
 "T50_C_Avg",
 "PA",
 "PA_2",
 "PA_3"


"""

VARCONV = {
           'vwc06_avg': 'vwc_06_avg',
           'vwc12_avg': 'vwc_12_avg',
           'vwc24_avg': 'vwc_24_avg',
           'vwc50_avg': 'vwc_50_avg',
           }

# stdlib
import os
import pytz
import datetime
import subprocess
import tempfile

# Third party
import psycopg2
ISUAG = psycopg2.connect(database='isuag',  host='iemdb')
icursor = ISUAG.cursor()

BASE = '/mnt/home/mesonet/sm/'
STATIONS = {'CAMI4': dict(daily='Calumet/Calumet_DailySI.dat',
                          hourly='Calumet/Calumet_HrlySI.dat'),
            'BOOI4': dict(daily='AEAFarm/AEAFarm_DailySI.dat',
                          hourly='AEAFarm/AEAFarm_HrlySI.dat'),
            'SLNI4': dict(daily='Wellman/Wellman_DailySI.dat',
                          hourly='Wellman/Wellman_HrlySI.dat'),
            'SBEI4': dict(daily='Ocheyedan/Ocheyedan_DailySI.dat',
                          hourly='Ocheyedan/Ocheyedan_HrlySI.dat'),
            }

def hourly_process(nwsli, maxts):
    """ Process the hourly file """
    fn = "%s%s" % (BASE, STATIONS[nwsli]['hourly'])
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
    for i in range(len(lines)-1, 3, -1):
        tokens = lines[i].strip().replace('"','').split(",")
        if len(tokens) != len(headers):
            continue
        valid = datetime.datetime.strptime(tokens[ headers.index('timestamp')],
                                           '%Y-%m-%d %H:%M:%S')
        valid = valid.replace(tzinfo=pytz.FixedOffset(-360))
        if valid <= maxts:
            break
        # We are ready for dbinserting!
        dbcols = "station,valid," + ",".join(headers[2:])
        dbvals = "'%s','%s-06'," % (nwsli, valid.strftime("%Y-%m-%d %H:%M:%S"))
        for v in tokens[2:]:
            dbvals += "%s," % (formatter(v),)
        sql = "INSERT into sm_hourly (%s) values (%s)" % (dbcols, dbvals[:-1])
        icursor.execute(sql)

def formatter(v):
    """ Something to format things nicely for SQL"""
    if v.find("NAN") > -1:
        return 'Null'
    if v.find(" ") > -1: #Timestamp
        return "'%s-06'" % (v,)
    return v

def daily_process(nwsli, maxts):
    """ Process the daily file """
    fn = "%s%s" % (BASE, STATIONS[nwsli]['daily'])
    if not os.path.isfile(fn):
        return
    lines = open(fn).readlines()
    if len(lines) < 6:
        return
    # Read header....
    headers = []
    for col in lines[1].strip().replace('"', '').split(","):
        headers.append(VARCONV.get(col.lower(), col.lower()))
    # Read data
    for i in range(len(lines)-1, 3, -1):
        tokens = lines[i].strip().replace('"','').split(",")
        if len(tokens) != len(headers):
            continue
        valid = datetime.datetime.strptime(tokens[ headers.index('timestamp')][:10],
                                           '%Y-%m-%d')
        valid = valid.date() - datetime.timedelta(days=1)
        if valid < maxts:
            break
        if valid == maxts: # Reprocess
            icursor.execute("""DELETE from sm_daily WHERE valid = '%s' and
            station = '%s' """ % (valid.strftime("%Y-%m-%d"), nwsli))
        # We are ready for dbinserting!
        dbcols = "station,valid," + ",".join(headers[2:])
        dbvals = "'%s','%s'," % (nwsli, valid.strftime("%Y-%m-%d"))
        for v in tokens[2:]:
            dbvals += "%s," % (formatter(v),)
        sql = "INSERT into sm_daily (%s) values (%s)" % (dbcols, dbvals[:-1])
        icursor.execute(sql)

def get_max_timestamps(nwsli):
    """ Fetch out our max values """
    data = {'hourly': datetime.datetime(2012, 1, 1, 
                                        tzinfo=pytz.FixedOffset(-360)), 
            'daily': datetime.date(2012, 1, 1)}
    icursor.execute("""SELECT max(valid) from sm_daily 
        WHERE station = '%s'""" % (nwsli, ))
    row = icursor.fetchone()
    if row[0] is not None:
        data['daily'] = row[0]

    icursor.execute("""SELECT max(valid) from sm_hourly 
        WHERE station = '%s'""" % (nwsli, ))
    row = icursor.fetchone()
    if row[0] is not None:
        data['hourly'] = row[0]
    return data

def dump_raw_to_ldm(nwsli):
    """ Send the raw datafile to LDM """
    fn = STATIONS[nwsli]['daily']
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
    tmpfp.write(lines[-3])
    tmpfp.write(lines[-2])
    tmpfp.write(lines[-1])
    tmpfp.close()
    cmd = "/home/ldm/bin/pqinsert -p 'data c %s csv/isusm/%s_daily.txt bogus txt' %s" % (
                    datetime.datetime.utcnow().strftime("%Y%m%d%H%M"), nwsli,
                    tmpfn)
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    p.stdout.read()
    os.remove(tmpfn)

    """ Send the raw datafile to LDM """
    fn = STATIONS[nwsli]['hourly']
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
    tmpfp.write(lines[-3])
    tmpfp.write(lines[-2])
    tmpfp.write(lines[-1])
    tmpfp.close()
    cmd = "/home/ldm/bin/pqinsert -p 'data c %s csv/isusm/%s_hourly.txt bogus txt' %s" % (
                    datetime.datetime.utcnow().strftime("%Y%m%d%H%M"), nwsli,
                    tmpfn)
    proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    proc.stdout.read()
    os.remove(tmpfn)


def main():
    """ Go main Go """
    for nwsli in STATIONS.keys():
        maxobs = get_max_timestamps(nwsli)
        hourly_process(nwsli, maxobs['hourly'])
        daily_process(nwsli, maxobs['daily'])
        dump_raw_to_ldm(nwsli)
    
    icursor.close()
    ISUAG.commit()
    ISUAG.close()
    
if __name__ == '__main__':
    main()