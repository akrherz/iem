"""
 Ingest ISU SOILM data!
 
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
import os
import iemdb
import iemtz
import datetime
ISUAG = iemdb.connect('isuag')
icursor = ISUAG.cursor()

STATIONS = {'CAMI4': dict(daily='/mnt/home/mesonet/sm/Calumet/Calumet_DailySI.dat',
                          hourly='/mnt/home/mesonet/sm/Calumet/Calumet_HrlySI.dat'),
            }

def hourly_process(nwsli, maxts):
    """ Process the hourly file """
    """ Process the daily file """
    fn = STATIONS[nwsli]['hourly']
    if not os.path.isfile(fn):
        return
    lines = open(fn).readlines()
    if len(lines) < 6:
        return
    # Read header....
    headers = []
    for col in lines[1].strip().replace('"', '').split(","):
        headers.append(col)
    # Read data
    for i in range(len(lines)-1,3,-1):
        tokens = lines[i].strip().replace('"','').split(",")
        if len(tokens) != len(headers):
            continue
        valid = datetime.datetime.strptime(tokens[ headers.index('TIMESTAMP')],
                                           '%Y-%m-%d %H:%M:%S')
        valid = valid.replace(tzinfo=iemtz.CentralDaylight)
        if valid <= maxts:
            break
        # We are ready for dbinserting!
        dbcols = "station,valid," + ",".join(headers[2:])
        dbvals = "'%s','%s-05'," % (nwsli, valid.strftime("%Y-%m-%d %H:%M:%S"))
        for v in tokens[2:]:
            dbvals += "%s," % (formatter(v),)
        sql = "INSERT into sm_hourly (%s) values (%s)" % (dbcols, dbvals[:-1])
        icursor.execute(sql)

def formatter(v):
    """ Something to format things nicely for SQL"""
    if v.find("NAN") > -1:
        return 'Null'
    if v.find(" ") > -1: #Timestamp
        return "'%s-05'" % (v,)
    return v

def daily_process(nwsli, maxts):
    """ Process the daily file """
    fn = STATIONS[nwsli]['daily']
    if not os.path.isfile(fn):
        return
    lines = open(fn).readlines()
    if len(lines) < 6:
        return
    # Read header....
    headers = []
    for col in lines[1].strip().replace('"', '').split(","):
        headers.append(col)
    # Read data
    for i in range(len(lines)-1,3,-1):
        tokens = lines[i].strip().replace('"','').split(",")
        if len(tokens) != len(headers):
            continue
        valid = datetime.datetime.strptime(tokens[ headers.index('TIMESTAMP')][:10],
                                           '%Y-%m-%d')
        valid = valid.date() - datetime.timedelta(days=1)
        if valid < maxts:
            break
        if valid == maxts: # Reprocess
            icursor.execute("""DELETE from sm_daily WHERE valid = '%s' and
            station = '%s' """ % (valid.strftime("%Y-%m-%d") ,nwsli))
        # We are ready for dbinserting!
        dbcols = "station,valid," + ",".join(headers[2:])
        dbvals = "'%s','%s-05'," % (nwsli, valid.strftime("%Y-%m-%d %H:%M:%S"))
        for v in tokens[2:]:
            dbvals += "%s," % (formatter(v),)
        sql = "INSERT into sm_daily (%s) values (%s)" % (dbcols, dbvals[:-1])
        icursor.execute(sql)

def get_max_timestamps(nwsli):
    """ Fetch out our max values """
    data = {'hourly': datetime.datetime(2012,1,1, tzinfo=iemtz.CentralDaylight), 
            'daily': datetime.date(2012,1,1)}
    icursor.execute("""SELECT max(valid) from sm_daily WHERE station = '%s'""" % (
                                                                nwsli,))
    row = icursor.fetchone()
    if row[0] is not None:
        data['daily'] = row[0]

    icursor.execute("""SELECT max(valid) from sm_hourly WHERE station = '%s'""" % (
                                                                nwsli,))
    row = icursor.fetchone()
    if row[0] is not None:
        data['hourly'] = row[0]
    return data

def main():
    for nwsli in STATIONS.keys():
        maxobs = get_max_timestamps(nwsli)
        hourly_process(nwsli, maxobs['hourly'])
        daily_process(nwsli, maxobs['daily'])
    
    icursor.close()
    ISUAG.commit()
    ISUAG.close()
    
if __name__ == '__main__':
    main()