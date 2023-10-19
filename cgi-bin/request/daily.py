"""Download IEM summary data!"""
import sys
from io import BytesIO, StringIO

import pandas as pd
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, get_sqlalchemy_conn
from pyiem.webutil import ensure_list, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


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
    clisites = []
    for station in stations:
        if station == "_ALL":
            for sid in nt.sts:
                clid = nt.sts[sid]["ncei91"]
                if clid not in clisites:
                    clisites.append(clid)
            break
        if station not in nt.sts:
            return f"ERROR: station: {station} not found in network: {network}"
        clid = nt.sts[station]["ncei91"]
        if clid not in clisites:
            clisites.append(clid)
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                """
            SELECT station, to_char(valid, 'mmdd') as sday,
            high as climo_high_f, low as climo_low_f,
            precip as climo_precip_in from ncei_climate91
            where station = ANY(:clisites)
            """
            ),
            conn,
            params={"clisites": clisites},
        )
    return df


def get_data(network, sts, ets, stations, cols, na, fmt):
    """Go fetch data please"""
    if not cols:
        cols = (
            "max_temp_f,min_temp_f,max_dewpoint_f,min_dewpoint_f,precip_in,"
            "avg_wind_speed_kts,avg_wind_drct,min_rh,avg_rh,max_rh,"
            "climo_high_f,climo_low_f,climo_precip_in,snow_in,snowd_in,"
            "min_feel,avg_feel,max_feel,max_wind_speed_kts,max_wind_gust_kts,"
            "srad_mj"
        ).split(",")
    cols.insert(0, "day")
    cols.insert(0, "station")
    climate = get_climate(network, stations)
    if isinstance(climate, str):
        return climate

    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            text(
                """
            SELECT id as station, day, max_tmpf as max_temp_f,
            min_tmpf as min_temp_f, max_dwpf as max_dewpoint_f,
            min_dwpf as min_dewpoint_f,
            pday as precip_in,
            avg_sknt as avg_wind_speed_kts,
            vector_avg_drct as avg_wind_drct,
            min_rh, avg_rh, max_rh,
            snow as snow_in,
            snowd as snowd_in,
            min_feel, avg_feel, max_feel,
            max_sknt as max_wind_speed_kts,
            max_gust as max_wind_gust_kts,
            srad_mj, ncei91, to_char(day, 'mmdd') as sday
            from summary s JOIN stations t
            on (t.iemid = s.iemid) WHERE
            s.day >= :st and s.day <= :et and
            t.network = :n and t.id = ANY(:ds)
            ORDER by day ASC"""
            ),
            conn,
            params={"st": sts, "et": ets, "n": network, "ds": stations},
        )
    # Join to climate data frame
    df = df.merge(
        climate,
        how="left",
        left_on=["ncei91", "sday"],
        right_on=["station", "sday"],
        suffixes=("", "_r"),
    )
    df = df[df.columns.intersection(cols)]
    if na != "blank":
        df = df.fillna(na)
    if fmt == "json":
        return df.to_json(orient="records")
    if fmt == "excel":
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df.to_excel(writer, "Data", index=False)
        return bio.getvalue()

    sio = StringIO()
    df.to_csv(sio, index=False)
    return sio.getvalue()


@iemapp()
def application(environ, start_response):
    """See how we are called"""
    if "sts" not in environ:
        raise IncompleteWebRequest("GET start time parameters missing.")
    sts, ets = environ["sts"].date(), environ["ets"].date()

    if sts.year != ets.year and overloaded():
        start_response(
            "503 Service Unavailable", [("Content-type", "text/plain")]
        )
        return [b"ERROR: server over capacity, please try later"]

    fmt = environ.get("format", "csv")
    stations = ensure_list(environ, "stations")
    if not stations:
        stations = ensure_list(environ, "station")
    if not stations:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"ERROR: No stations specified for request"]
    network = environ.get("network")[:12]
    cols = ensure_list(environ, "var")
    na = environ.get("na", "None")
    if na not in ["M", "None", "blank"]:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"ERROR: Invalid `na` value provided. {M, None, blank}"]
    if fmt != "excel":
        start_response("200 OK", [("Content-type", "text/plain")])
        return [
            get_data(network, sts, ets, stations, cols, na, fmt).encode(
                "ascii"
            )
        ]
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=daily.xlsx"),
    ]
    start_response("200 OK", headers)
    return [get_data(network, sts, ets, stations, cols, na, fmt)]
