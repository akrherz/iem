"""
My purpose in life is to update the hourly_YYYY with observed or
computed hourly precipitation
"""
import datetime
import psycopg2
import sys
import pytz


def archive(ts):
    """Reprocess an older date

    Currently, we only support the METAR database :(
    """
    asos = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    acursor = asos.cursor()
    iem = psycopg2.connect(database='iem', host='iemdb')
    icursor = iem.cursor()

    table = "t%s" % (ts.year,)
    acursor.execute("""WITH data as (
        SELECT station, max(p01i) from """ + table + """
        WHERE valid > %s and valid <= %s and p01i is not null
        GROUP by station)

    SELECT station, network, max, iemid from data d JOIN stations s on
    (d.station = s.id) WHERE (s.network ~* 'ASOS' or s.network = 'AWOS')
    """, (ts, ts + datetime.timedelta(minutes=60)))

    table = "hourly_%s" % (ts.year,)
    for row in acursor:
        icursor.execute("""INSERT into """ + table + """
        (station, network, valid, phour, iemid)
        VALUES (%s, %s, %s, %s, %s)
        """, (row[0], row[1], ts, row[2], row[3]))

    icursor.close()
    iem.commit()


def realtime(ts):
    IEM = psycopg2.connect(database='iem', host='iemdb')
    icursor = IEM.cursor()
    table = "hourly_%s" % (ts.year,)
    icursor.execute("""
    INSERT into """ + table + """
        (SELECT t.id, t.network, %s as v, max(phour) as p, t.iemid
        from current_log c, stations t WHERE
            (valid - '1 minute'::interval) >= %s
            and (valid - '1 minute'::interval) < %s
            and phour >= 0 and
            t.network NOT IN ('KCCI','KELO','KIMT')
            and c.iemid = t.iemid
            and t.network !~* 'DCP'
            GROUP by t,id, t.network, v, t.iemid)
            """, (ts, ts, ts + datetime.timedelta(minutes=60)))
    IEM.commit()
    IEM.close()


def main(argv):
    """Do things"""
    if len(argv) == 5:
        # Run for a custom hour
        ts = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]),
                               int(argv[4]))
        ts = ts.replace(tzinfo=pytz.utc)
        archive(ts)
    else:
        # We run for the last hour
        ts = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        ts = ts.replace(minutes=0, seconds=0, microseconds=0,
                        tzinfo=pytz.utc)
        realtime(ts)

if __name__ == '__main__':
    main(sys.argv)
