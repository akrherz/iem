#!/usr/bin/env python
"""Download IEM summary data!"""
import cgi
import os
import datetime

from pyiem.util import get_dbconn, ssw
from pyiem.network import Table as NetworkTable


def get_climate(network, stations):
    """Fetch the climatology for these stations"""
    nt = NetworkTable(network)
    if not nt.sts:
        ssw("ERROR: Invalid network specified")
        return
    data = dict()
    clisites = []
    cldata = dict()
    for station in stations:
        if station not in nt.sts:
            ssw("ERROR: station: %s not found in network: %s" % (
                station, network))
            return
        cldata[nt.sts[station]['ncdc81']] = dict()
        clisites.append(nt.sts[station]['ncdc81'])
    if not clisites:
        return data
    if len(clisites) == 1:
        clisites.append('XX')
    mesosite = get_dbconn('coop')
    cursor = mesosite.cursor()
    cursor.execute("""
        SELECT station, valid, high, low, precip
        from ncdc_climate81 where station in %s
    """, (tuple(clisites),))
    for row in cursor:
        cldata[row[0]][row[1].strftime("%m%d")] = {'high': row[2],
                                                   'low': row[3],
                                                   'precip': row[4]}
    sts = datetime.datetime(2000, 1, 1)
    ets = datetime.datetime(2001, 1, 1)
    for stid in stations:
        data[stid] = dict()
        now = sts
        clsite = nt.sts[stid]['ncdc81']
        while now < ets:
            key = now.strftime("%m%d")
            data[stid][key] = cldata[clsite].get(key, dict(high='M', low='M',
                                                           precip='M'))
            now += datetime.timedelta(days=1)
    return data


def get_data(network, sts, ets, stations):
    """Go fetch data please"""
    pgconn = get_dbconn('iem')
    cursor = pgconn.cursor()
    climate = get_climate(network, stations)
    if climate is None:
        return ""
    res = ("station,day,max_temp_f,min_temp_f,max_dewpoint_f,"
           "min_dewpoint_f,precip_in,avg_wind_speed_kts,avg_wind_drct,"
           "min_rh,avg_rh,max_rh,climo_high_f,climo_low_f,climo_precip_in,"
           "snow_in,snowd_in,min_feel,avg_feel,max_feel\n")
    if len(stations) == 1:
        stations.append('ZZZZZ')
    cursor.execute("""SELECT id, day, max_tmpf, min_tmpf, max_dwpf, min_dwpf,
        pday, avg_sknt, vector_avg_drct, min_rh, avg_rh, max_rh, snow,
        snowd, min_feel, avg_feel, max_feel
        from summary s JOIN stations t
        on (t.iemid = s.iemid) WHERE
        s.day >= %s and s.day < %s and t.network = %s and t.id in %s
        ORDER by day ASC""", (sts, ets, network, tuple(stations)))
    for row in cursor:
        res += ("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"
                ) % (row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                     row[7], row[8], row[9], row[10], row[11],
                     climate[row[0]][row[1].strftime("%m%d")]['high'],
                     climate[row[0]][row[1].strftime("%m%d")]['low'],
                     climate[row[0]][row[1].strftime("%m%d")]['precip'],
                     row[12], row[13], row[14], row[15], row[16])

    return res


def main(form):
    """See how we are called"""
    sts = datetime.date(int(form.getfirst('year1')),
                        int(form.getfirst('month1')),
                        int(form.getfirst('day1')))
    ets = datetime.date(int(form.getfirst('year2')),
                        int(form.getfirst('month2')),
                        int(form.getfirst('day2')))

    ssw('Content-type: text/plain\n\n')
    stations = form.getlist('stations')
    if not stations:
        stations = form.getlist('station')
    if not stations:
        ssw("ERROR: No stations specified for request")
        return
    network = form.getfirst('network')[:12]
    ssw(get_data(network, sts, ets, stations))


if __name__ == '__main__':
    # Go
    main(cgi.FieldStorage())


def test_simple():
    """Can we do simple things."""
    os.environ['QUERY_STRING'] = (
        "year1=2019&month1=1&day1=1&year2=2019&month2=2&day2=1"
    )
    main(cgi.FieldStorage(environ=os.environ))
