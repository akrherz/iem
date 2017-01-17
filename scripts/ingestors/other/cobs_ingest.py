"""Ingest the COBS data file

  Run from RUN_20_AFTER.sh
"""
import pandas as pd
import psycopg2
import pytz
import datetime
import os
from pyiem.observation import Observation

SID = 'OT0012'
DIRPATH = "/mnt/mesonet/home/mesonet/ot/ot0005/incoming/Pederson"

HOURLYCONV = {'Batt_Volt': 'battery',
              'PTemp_C': None,
              'Rain_in_Tot': 'phour',
              'SlrW_Avg': 'srad',
              'SlrMJ_Tot': None,
              'AirTF_Avg': 'tmpf',
              'RH': 'relh',
              'WS_mph_Avg': None,  # TODO
              'WS_mph_Max': None,
              'WindDir': 'drct',
              'WS_mph_S_WVT': None,
              'WindDir_D1_WVT': None,
              'T107_F_Avg': None}

DAILYCONV = {'Batt_Volt_Min': None,
             'PTemp_C_Max': None,
             'PTemp_C_Min': None,
             'Rain_in_Tot': 'pday',
             'SlrW_Avg': None,
             'SlrW_Max': None,
             'SlrW_TMx': None,
             'SlrMJ_Tot': None,
             'AirTF_Max': 'max_tmpf',
             'AirTF_TMx': None,
             'AirTF_Min': 'min_tmpf',
             'AirTF_TMn': None,
             'AirTF_Avg': None,
             'RH_Max': 'max_rh',
             'RH_TMx': None,
             'RH_Min': 'min_rh',
             'RH_TMn': None,
             'WS_mph_Max': None,
             'WS_mph_TMx': None,
             'WS_mph_S_WVT': None,
             'WindDir_D1_WVT': None,
             'T107_F_Max': None,
             'T107_F_TMx': None,
             'T107_F_Min': None,
             'T107_F_TMn': None,
             'T107_F_Avg': None}


def database(lastob, ddf, hdf):
    """Do the tricky database work"""
    # This should be okay as we are always going to CST
    maxts = hdf['TIMESTAMP'].max().replace(
        tzinfo=pytz.timezone("America/Chicago"))
    if maxts <= lastob:
        # print("maxts: %s lastob: %s" % (maxts, lastob))
        return
    iemdb = psycopg2.connect(database='iem', host='iemdb')
    icursor = iemdb.cursor()
    df2 = hdf[hdf['valid'] > lastob]
    for _, row in df2.iterrows():
        localts = row['valid'].tz_convert(pytz.timezone("America/Chicago"))
        # Find, if it exists, the summary table entry here
        daily = ddf[ddf['date'] == localts.date()]
        ob = Observation(SID, 'OT', localts)
        if len(daily.index) == 1:
            for key, value in DAILYCONV.items():
                if value is None:
                    continue
                # print("D: %s -> %s" % (key, value))
                ob.data[value] = daily.iloc[0][key]
        for key, value in HOURLYCONV.items():
            if value is None:
                continue
            # print("H: %s -> %s" % (key, value))
            ob.data[value] = row[key]
        ob.save(icursor)
    icursor.close()
    iemdb.commit()


def get_last():
    pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    cursor = pgconn.cursor()
    cursor.execute("""SELECT valid at time zone 'UTC'
    from current c JOIN stations t
    ON (c.iemid = t.iemid) where t.id = %s
    """, (SID,))
    return cursor.fetchone()[0].replace(tzinfo=pytz.utc)


def process(lastob):
    now = datetime.datetime.now()
    dailyfn = "%s/%s/Daily.dat" % (DIRPATH, now.year)
    hourlyfn = "%s/%s/Hourly.dat" % (DIRPATH, now.year)
    if not os.path.isfile(dailyfn):
        print("cobs_ingest.py missing %s" % (dailyfn,))
        return
    if not os.path.isfile(hourlyfn):
        print("cobs_ingest.py missing %s" % (hourlyfn,))
        return

    ddf = pd.read_csv(dailyfn, header=0,
                      skiprows=[0, 2, 3], quotechar='"', warn_bad_lines=True)
    ddf['TIMESTAMP'] = pd.to_datetime(ddf['TIMESTAMP'])
    # Timestamps should be moved back one day
    ddf['date'] = (ddf['TIMESTAMP'] - datetime.timedelta(hours=12)).dt.date
    hdf = pd.read_csv(hourlyfn, header=0,
                      skiprows=[0, 2, 3], quotechar='"', warn_bad_lines=True)
    hdf['TIMESTAMP'] = pd.to_datetime(hdf['TIMESTAMP'])
    # Move all timestamps to UTC +6
    hdf['valid'] = (hdf['TIMESTAMP'] +
                    datetime.timedelta(hours=6)).dt.tz_localize('UTC')
    database(lastob, ddf, hdf)


def main():
    lastob = get_last()
    process(lastob)

if __name__ == '__main__':
    main()
