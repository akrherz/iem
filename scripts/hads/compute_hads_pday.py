"""Attempt at totalling up hourly DCP data """
import psycopg2
import datetime
import pytz
import sys
import numpy as np
from pandas.io.sql import read_sql


def do(date):
    """Do the necessary work for this date"""
    pgconn = psycopg2.connect(database='hads', host='iemdb', user='nobody')
    iem_pgconn = psycopg2.connect(database='iem', host='iemdb')
    icursor = iem_pgconn.cursor()
    df = read_sql("""
    SELECT id, iemid, tzname from stations where network ~* 'DCP'
    """, pgconn, index_col='id')
    bases = {}
    for tzname in df['tzname'].unique():
        ts = datetime.datetime(date.year, date.month, date.day, 12)
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        base = ts.astimezone(pytz.timezone(tzname))
        bases[tzname] = base.replace(hour=0)
    # retreive data that is within 12 hours of our bounds
    sts = datetime.datetime(date.year, date.month,
                            date.day) - datetime.timedelta(hours=12)
    ets = sts + datetime.timedelta(hours=48)
    obsdf = read_sql("""
    SELECT distinct station, valid at time zone 'UTC' as utc_valid, value
    from raw"""+str(date.year)+""" WHERE valid between %s and %s and
    substr(key, 1, 3) = 'PPH' and value >= 0
    """, pgconn, params=(sts, ets), index_col=None)
    obsdf['utc_valid'] = obsdf['utc_valid'].dt.tz_localize('utc')
    precip = np.zeros((24*60))
    for station in obsdf['station'].unique():
        precip[:] = 0
        stdf = obsdf[obsdf['station'] == station].copy()
        if station not in df.index:
            continue
        tz = df.loc[station, 'tzname']
        for _, row in stdf.iterrows():
            ts = row['utc_valid'].to_datetime()
            if ts <= bases[tz]:
                continue
            t1 = (ts - bases[tz]).total_seconds() / 60.
            t0 = max([0, t1 - 60.])
            precip[t0:t1] = row['value'] / 60.
        pday = np.sum(precip)
        if pday > 50:
            continue
        iemid = df.loc[station, 'iemid']
        icursor.execute("""UPDATE summary_"""+str(date.year)+"""
        SET pday = %s WHERE iemid = %s and day = %s and %s > coalesce(pday,0)
        """, (pday, iemid, date, pday))
        if icursor.rowcount == 0:
            print("Adding record %s[%s] for day %s" % (station, iemid, date))
            icursor.execute("""INSERT into summary_"""+str(date.year)+"""
            (iemid, day) VALUES (%s, %s)
            """, (iemid, date))
            icursor.execute("""UPDATE summary_"""+str(date.year)+"""
            SET pday = %s WHERE iemid = %s and day = %s
            and %s > coalesce(pday, 0)
            """, (pday, iemid, date, pday))
    icursor.close()
    iem_pgconn.commit()


def main(argv):
    """Do Something"""
    if len(argv) == 4:
        ts = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    else:
        ts = datetime.date.today()
    do(ts)

if __name__ == '__main__':
    main(sys.argv)
