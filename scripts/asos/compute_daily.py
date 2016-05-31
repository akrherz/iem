"""Compute daily summaries of ASOS/METAR data

Called from RUN_12Z.sh for the previous date
"""
import psycopg2
import sys
import datetime
from pyiem.datatypes import speed, direction, temperature
from pyiem import meteorology


def clean_rh(val):
    """Make sure RH values are always sane"""
    if val > 100. or val < 1:
        return None
    return val


def do(ts):
    """Process this date timestamp"""
    asos = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = asos.cursor()
    iemaccess = psycopg2.connect(database='iem', host='iemdb')
    icursor = iemaccess.cursor()
    cursor.execute("""
    select station, network, iemid, drct, sknt, valid at time zone tzname,
    tmpf, dwpf from
    alldata d JOIN stations t on (t.id = d.station)
    where (network ~* 'ASOS' or network = 'AWOS')
    and valid between %s and %s and t.tzname is not null
    ORDER by valid ASC
    """, (ts - datetime.timedelta(days=2), ts + datetime.timedelta(days=2)))
    wdata = dict()
    rhdata = dict()
    for row in cursor:
        if row[5].strftime("%m%d") != ts.strftime("%m%d"):
            continue
        station = "%s|%s|%s" % (row[0], row[1], row[2])
        if row[6] is not None and row[7] is not None:
            tmpf = temperature(row[6], 'F')
            dwpf = temperature(row[7], 'F')
            rh = meteorology.relh(tmpf, dwpf)
            if station not in rhdata:
                rhdata[station] = dict(valid=[], rh=[])
            rhdata[station]['valid'].append(row[5])
            rhdata[station]['rh'].append(rh.value('%'))
        if row[4] is not None and row[3] is not None:
            sknt = speed(row[4], 'KT')
            drct = direction(row[3], 'DEG')
            (u, v) = meteorology.uv(sknt, drct)
            if station not in wdata:
                wdata[station] = {'valid': [], 'sknt': [], 'u': [], 'v': []}
            wdata[station]['valid'].append(row[5])
            wdata[station]['sknt'].append(row[4])
            wdata[station]['u'].append(u.value('KT'))
            wdata[station]['v'].append(v.value('KT'))

    table = "summary_%s" % (ts.year,)
    for stid in rhdata:
        # Not enough data
        if len(rhdata[stid]['valid']) < 6:
            continue
        station, network, iemid = stid.split("|")
        now = datetime.datetime(ts.year, ts.month, ts.day)
        runningrh = 0
        runningtime = 0
        for i, valid in enumerate(rhdata[stid]['valid']):
            delta = (valid - now).seconds
            runningtime += delta
            runningrh += (delta * rhdata[stid]['rh'][i])
            now = valid

        if runningtime == 0:
            print(("compute_daily %s has time domain %s %s"
                   ) % (stid, rhdata[stid]['valid'][0],
                        rhdata[stid]['valid'][-1]))
            continue
        avg_rh = clean_rh(runningrh / runningtime)
        min_rh = clean_rh(min(rhdata[stid]['rh']))
        max_rh = clean_rh(max(rhdata[stid]['rh']))

        def do_update():
            icursor.execute("""UPDATE """ + table + """
            SET avg_rh = %s, min_rh = %s, max_rh = %s WHERE
            iemid = %s and day = %s""", (avg_rh, min_rh, max_rh, iemid, ts))
        do_update()
        if icursor.rowcount == 0:
            print(('compute_daily Adding %s for %s %s %s'
                   ) % (table, station, network, ts))
            icursor.execute("""INSERT into """ + table + """
            (iemid, day) values (%s, %s)""", (iemid, ts))
            do_update()

    for stid in wdata:
        # Not enough data
        if len(wdata[stid]['valid']) < 6:
            continue
        station, network, iemid = stid.split("|")
        now = datetime.datetime(ts.year, ts.month, ts.day)
        runningsknt = 0
        runningtime = 0
        runningu = 0
        runningv = 0
        for i, valid in enumerate(wdata[stid]['valid']):
            delta = (valid - now).seconds
            runningtime += delta
            runningsknt += (delta * wdata[stid]['sknt'][i])
            runningu += (delta * wdata[stid]['u'][i])
            runningv += (delta * wdata[stid]['v'][i])
            now = valid

        if runningtime == 0:
            print(("compute_daily %s has time domain %s %s"
                   ) % (stid, wdata[stid]['valid'][0],
                        wdata[stid]['valid'][-1]))
            continue
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
            print(('compute_daily Adding %s for %s %s %s'
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
