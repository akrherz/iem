"""Compute average wind speeds for usage in IEM Access

Called from RUN_12Z.sh for the previous date
"""
import psycopg2
import sys
import datetime
from pyiem.datatypes import speed, direction
from pyiem import meteorology


def do(ts):
    """Process this date timestamp"""
    asos = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = asos.cursor()
    iemaccess = psycopg2.connect(database='iem', host='iemdb')
    icursor = iemaccess.cursor()
    cursor.execute("""
    select station, network, iemid, drct, sknt, valid at time zone tzname from
    alldata d JOIN stations t on (t.id = d.station)
    where (network ~* 'ASOS' or network = 'AWOS')
    and valid between %s and %s and drct is not null and sknt is not null
    ORDER by valid ASC
    """, (ts - datetime.timedelta(days=2), ts + datetime.timedelta(days=2)))
    data = {}
    for row in cursor:
        if row[5].strftime("%m%d") != ts.strftime("%m%d"):
            continue
        sknt = speed(row[4], 'KT')
        drct = direction(row[3], 'DEG')
        (u, v) = meteorology.uv(sknt, drct)
        station = "%s|%s|%s" % (row[0], row[1], row[2])
        if station not in data:
            data[station] = {'valid': [], 'sknt': [], 'u': [], 'v': []}
        data[station]['valid'].append(row[5])
        data[station]['sknt'].append(row[4])
        data[station]['u'].append(u.value('KT'))
        data[station]['v'].append(v.value('KT'))

    table = "summary_%s" % (ts.year,)
    for stid in data:
        # Not enough data
        if len(data[stid]['valid']) < 6:
            continue
        station, network, iemid = stid.split("|")
        now = datetime.datetime(ts.year, ts.month, ts.day)
        runningsknt = 0
        runningtime = 0
        runningu = 0
        runningv = 0
        for i, valid in enumerate(data[stid]['valid']):
            delta = (valid - now).seconds
            runningtime += delta
            runningsknt += (delta * data[stid]['sknt'][i])
            runningu += (delta * data[stid]['u'][i])
            runningv += (delta * data[stid]['v'][i])
            now = valid

        sknt = runningsknt / runningtime
        u = speed(runningu / runningtime, 'KT')
        v = speed(runningv / runningtime, 'KT')
        drct = meteorology.drct(u, v).value("DEG")

        def do_update():
            icursor.execute("""UPDATE """ + table + """
            SET avg_sknt = %s, vector_avg_drct = %s WHERE
            iemid = %s and day = %s""", (sknt, drct, iemid, ts))
        do_update()
        if icursor.rowcount == 0:
            print(('compute_avg_winds Adding %s for %s %s %s'
                   ) % (table, station, network, ts))
            icursor.execute("""INSERT into """ + table + """
            (iemid, day) values (%s, %s)""", (iemid, ts))
            do_update()

    icursor.close()
    iemaccess.commit()
    iemaccess.close()


def main():
    """Go Main Go"""
    ts = datetime.date.today() - datetime.timedelta(days=1)
    if len(sys.argv) == 4:
        ts = datetime.date(int(sys.argv[1]), int(sys.argv[2]),
                           int(sys.argv[3]))
    do(ts)

if __name__ == '__main__':
    main()
