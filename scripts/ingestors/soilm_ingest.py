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
           'calcvwc06_avg': 'vwc_06_avg',
        'calcvwc12_avg': 'vwc_12_avg',
            'calcvwc24_avg': 'vwc_24_avg',
            'calcvwc50_avg': 'vwc_50_avg',
           }

# stdlib
import os
import pytz
import datetime
import subprocess
import tempfile

# Third party
from pyiem.observation import Observation
from pyiem.datatypes import temperature, humidity
import pyiem.meteorology as met
import psycopg2
ISUAG = psycopg2.connect(database='isuag',  host='iemdb')
icursor = ISUAG.cursor()

ACCESS = psycopg2.connect(database='iem', host='iemdb')
accesstxn = ACCESS.cursor()

BASE = '/mnt/home/loggernet/'
STATIONS = {'CAMI4': dict(daily='Calumet/Calumet_DailySI.dat',
                          hourly='Calumet/Calumet_HrlySI.dat'),
            'BOOI4': dict(daily='AEAFarm/AEAFarm_DailySI.dat',
                          hourly='AEAFarm/AEAFarm_HrlySI.dat'),
            'WMNI4': dict(daily='Wellman/Wellman_DailySI.dat',
                          hourly='Wellman/Wellman_HrlySI.dat'),
            'SBEI4': dict(daily='Sibley/Sibley_DailySI.dat',
                          hourly='Sibley/Sibley_HrlySI.dat'),
            'NASI4': dict(daily='Nashua/Nashua_DailySI.dat',
                          hourly='Nashua/Nashua_HrlySI.dat'),
            'OKLI4': dict(daily='Lewis/Lewis_DailySI.dat',
                          hourly='Lewis/Lewis_HrlySI.dat'),
            'WTPI4': dict(daily='WestPoint/WestPoint_DailySI.dat',
                          hourly='WestPoint/WestPoint_HrlySI.dat'),
            'DONI4': dict(daily='Doon/Doon_DailySI.dat',
                          hourly='Doon/Doon_HrlySI.dat'),
            'KNAI4': dict(daily='Kanawha/Kanawha_DailySI.dat',
                          hourly='Kanawha/Kanawha_HrlySI.dat'),
            'GREI4': dict(daily='Greenfield/Greenfield_DailySI.dat',
                          hourly='Greenfield/Greenfield_HrlySI.dat'),
            'NWLI4': dict(daily='Newell/Newell_DailySI.dat',
                          hourly='Newell/Newell_HrlySI.dat'),
            'AEEI4': dict(daily='Ames/Ames_DailySI.dat',
                          hourly='Ames/Ames_HrlySI.dat'),
            'CNAI4': dict(daily='Castana/Castana_DailySI.dat',
                          hourly='Castana/Castana_HrlySI.dat'),
            'CHAI4': dict(daily='Chariton/Chariton_DailySI.dat',
                          hourly='Chariton/Chariton_HrlySI.dat'),
            'CRFI4': dict(daily='Crawfordsville/Crawfordsville_DailySI.dat',
                          hourly='Crawfordsville/Crawfordsville_HrlySI.dat'),
            'FRUI4': dict(daily='Muscatine/Muscatine_DailySI.dat',
                          hourly='Muscatine/Muscatine_HrlySI.dat'),
            'CIRI4': dict(daily='CedarRapids/CedarRapids_DailySI.dat',
                          hourly='CedarRapids/CedarRapids_HrlySI.dat'),
            }


def hourly_process(nwsli, maxts):
    """ Process the hourly file """
    #print '-------------- HOURLY PROCESS ---------------'
    fn = "%s%s" % (BASE, STATIONS[nwsli]['hourly'].split("/")[1])
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
        tokens = lines[i].strip().replace('"','').split(",")
        if len(tokens) != len(headers):
            continue
        valid = datetime.datetime.strptime(tokens[ headers.index('timestamp')],
                                           '%Y-%m-%d %H:%M:%S')
        valid = valid.replace(tzinfo=pytz.FixedOffset(-360))
        if valid <= maxts:
            break
        #print valid, tokens[ headers.index('timestamp')]
        # We are ready for dbinserting!
        dbcols = "station,valid," + ",".join(headers[2:])
        dbvals = "'%s','%s-06'," % (nwsli, valid.strftime("%Y-%m-%d %H:%M:%S"))
        for v in tokens[2:]:
            dbvals += "%s," % (formatter(v),)
        sql = "INSERT into sm_hourly (%s) values (%s)" % (dbcols, dbvals[:-1])
        icursor.execute(sql)

        # Update IEMAccess
        #print nwsli, valid
        ob = Observation(nwsli, 'ISUSM', 
                         valid.astimezone(pytz.timezone("America/Chicago")))
        tmpc = temperature(float(tokens[headers.index('tair_c_avg')]), 'C')
        if tmpc.value('F') > -50 and tmpc.value('F') < 140:
            ob.data['tmpf'] = tmpc.value('F')
            relh = humidity(float(tokens[headers.index('rh')]), '%')
            ob.data['relh'] = relh.value('%')
            ob.data['dwpf'] = met.dewpoint(tmpc, relh).value('F')
        ob.data['srad'] = tokens[headers.index('slrkw_avg')]
        ob.data['phour'] = float(tokens[headers.index('rain_mm_tot')]) / 24.5
        ob.data['sknt'] = float(tokens[headers.index('ws_mps_s_wvt')]) * 1.94
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
        #    print 'soilm_ingest.py station: %s ts: %s hrly updated no data?' % (
        #                                        nwsli, valid)
        processed += 1
    return processed

def formatter(v):
    """ Something to format things nicely for SQL"""
    if v.find("NAN") > -1:
        return 'Null'
    if v.find(" ") > -1: #Timestamp
        return "'%s-06'" % (v,)
    return v


def daily_process(nwsli, maxts):
    """ Process the daily file """
    # print '-------------- DAILY PROCESS ----------------'
    fn = "%s%s" % (BASE, STATIONS[nwsli]['daily'].split("/")[1])
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

        # Need a timezone
        valid = datetime.datetime(valid.year, valid.month, valid.day, 12, 0)
        valid = valid.replace(tzinfo=pytz.timezone("America/Chicago"))
        ob = Observation(nwsli, 'ISUSM', valid)
        ob.data['max_tmpf'] = temperature(
                    float(tokens[headers.index('tair_c_max')]), 'C').value('F')
        ob.data['min_tmpf'] = temperature(
                    float(tokens[headers.index('tair_c_min')]), 'C').value('F')
        ob.data['pday'] = float(tokens[headers.index('rain_mm_tot')]) / 24.5
        ob.data['et_inch'] = float(tokens[headers.index('dailyet')]) / 24.5
        ob.data['srad_mj'] = float(tokens[headers.index('slrmj_tot')])
        ob.data['max_sknt'] = float(tokens[headers.index('ws_mps_max')]) * 1.94
        ob.save(accesstxn)
        #    print 'soilm_ingest.py station: %s ts: %s daily updated no data?' % (
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

def dump_raw_to_ldm(nwsli, dyprocessed, hrprocessed):
    """ Send the raw datafile to LDM """
    fn = "%s%s" % (BASE, STATIONS[nwsli]['daily'].split("/")[1])
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
    cmd = "/home/ldm/bin/pqinsert -p 'data c %s csv/isusm/%s_daily.txt bogus txt' %s" % (
                    datetime.datetime.utcnow().strftime("%Y%m%d%H%M"), nwsli,
                    tmpfn)
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    p.stdout.read()
    os.remove(tmpfn)

    """ Send the raw datafile to LDM """
    fn = "%s%s" % (BASE, STATIONS[nwsli]['hourly'].split("/")[1])
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
        hrprocessed = hourly_process(nwsli, maxobs['hourly'])
        dyprocessed = daily_process(nwsli, maxobs['daily'])
        if hrprocessed > 0:
            dump_raw_to_ldm(nwsli, dyprocessed, hrprocessed)
        #else:
        #    print 'No LDM data sent for %s' % (nwsli,)
    update_pday()
    icursor.close()
    ISUAG.commit()
    ISUAG.close()
    
    accesstxn.close()
    ACCESS.commit()
    ACCESS.close()
    
if __name__ == '__main__':
    main()
