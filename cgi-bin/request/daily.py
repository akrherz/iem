"""Download IEM summary data!"""
from io import StringIO
import datetime
import sys

import pandas as pd
from paste.request import parse_formvars
from pyiem.util import get_dbconn
from pyiem.network import Table as NetworkTable


def overloaded():
    """Prevent automation from overwhelming the server"""

    with get_dbconn("iem") as pgconn:
        cursor = pgconn.cursor()
        cursor.execute("select one::float from system_loadavg")
        val = cursor.fetchone()[0]
    if val > 25:  # Cut back on logging
        sys.stderr.write(f"/cgi-bin/request/daily.py over cpu thres: {val}\n")
    return val > 20


def get_climate(network, stations):
    """Fetch the climatology for these stations"""
    nt = NetworkTable(network, only_online=False)
    if not nt.sts:
        return "ERROR: Invalid network specified"
    data = {}
    clisites = []
    cldata = {}
    for station in stations:
        if station not in nt.sts:
            return f"ERROR: station: {station} not found in network: {network}"
        clid = nt.sts[station]["ncei91"]
        cldata[clid] = {}
        if clid not in clisites:
            clisites.append(clid)
    if not clisites:
        return data
    mesosite = get_dbconn("coop")
    cursor = mesosite.cursor()
    cursor.execute(
        "SELECT station, valid, high, low, precip from ncei_climate91 "
        "where station in %s",
        (tuple(clisites),),
    )
    for row in cursor:
        cldata[row[0]][row[1].strftime("%m%d")] = {
            "high": row[2],
            "low": row[3],
            "precip": row[4],
        }
    sts = datetime.datetime(2000, 1, 1)
    ets = datetime.datetime(2001, 1, 1)
    for stid in stations:
        data[stid] = {}
        now = sts
        clsite = nt.sts[stid]["ncei91"]
        while now < ets:
            key = now.strftime("%m%d")
            data[stid][key] = cldata[clsite].get(
                key, dict(high="M", low="M", precip="M")
            )
            now += datetime.timedelta(days=1)
    return data


def get_data(network, sts, ets, stations, fmt):
    """Go fetch data please"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor("mystream")
    climate = get_climate(network, stations)
    if not isinstance(climate, dict):
        return climate
    sio = StringIO()
    sio.write(
        "station,day,max_temp_f,min_temp_f,max_dewpoint_f,"
        "min_dewpoint_f,precip_in,avg_wind_speed_kts,avg_wind_drct,"
        "min_rh,avg_rh,max_rh,climo_high_f,climo_low_f,climo_precip_in,"
        "snow_in,snowd_in,min_feel,avg_feel,max_feel,max_wind_speed_kts,"
        "max_wind_gust_kts\n"
    )
    if len(stations) == 1:
        stations.append("ZZZZZ")
    cursor.execute(
        """SELECT id, day, max_tmpf, min_tmpf, max_dwpf, min_dwpf,
        pday, avg_sknt, vector_avg_drct, min_rh, avg_rh, max_rh, snow,
        snowd, min_feel, avg_feel, max_feel, max_sknt, max_gust
        from summary s JOIN stations t
        on (t.iemid = s.iemid) WHERE
        s.day >= %s and s.day <= %s and t.network = %s and t.id in %s
        ORDER by day ASC""",
        (sts, ets, network, tuple(stations)),
    )
    for row in cursor:
        key = row[1].strftime("%m%d")
        sio.write(
            f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},"
            f"{row[7]},{row[8]},{row[9]},{row[10]},{row[11]},"
            f"{climate[row[0]][key]['high']},{climate[row[0]][key]['low']},"
            f"{climate[row[0]][key]['precip']},{row[12]},{row[13]},{row[14]},"
            f"{row[15]},{row[16]},{row[17]},{row[18]}\n"
        )
    if fmt == "json":
        sio.seek(0)
        df = pd.read_csv(sio, index_col=None, parse_dates=False)
        return df.to_json(orient="records")

    return sio.getvalue()


def application(environ, start_response):
    """See how we are called"""
    form = parse_formvars(environ)
    sts = datetime.date(
        int(form.get("year1")), int(form.get("month1")), int(form.get("day1"))
    )
    ets = datetime.date(
        int(form.get("year2")), int(form.get("month2")), int(form.get("day2"))
    )
    if sts.year != ets.year and overloaded():
        start_response(
            "503 Service Unavailable", [("Content-type", "text/plain")]
        )
        return [b"ERROR: server over capacity, please try later"]

    start_response("200 OK", [("Content-type", "text/plain")])
    stations = form.getall("stations")
    if not stations:
        stations = form.getall("station")
    if not stations:
        return [b"ERROR: No stations specified for request"]
    network = form.get("network")[:12]
    fmt = form.get("format", "text")
    return [get_data(network, sts, ets, stations, fmt).encode("ascii")]
