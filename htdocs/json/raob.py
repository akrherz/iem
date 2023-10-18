"""JSON service that emits RAOB profiles in JSON format

{'profiles': [
  {
  'station': 'OAX',
  'valid': '2013-08-21T12:00:00Z',
  'profile': [
    {'tmpc':99, 'pres': 99, 'dwpc': 99, 'sknt': 99, 'drct': 99, 'hght': 99},
    {'tmpc':99, 'pres': 99, 'dwpc': 99, 'sknt': 99, 'drct': 99, 'hght': 99},
    {...}
              ]
  },
  {...}]
}
"""
import datetime
import json
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_sqlalchemy_conn, html_escape
from pyiem.webutil import iemapp
from pymemcache.client import Client
from sqlalchemy import text

json.encoder.FLOAT_REPR = lambda o: format(o, ".2f")


def safe(val):
    """Be careful"""
    if val is None or np.isnan(val):
        return None
    return float(val)


def run(ts, sid, pressure):
    """Actually do some work!"""
    res = {"profiles": []}
    if ts.year > datetime.datetime.utcnow().year or ts.year < 1946:
        return json.dumps(res)

    stationlimiter = ""
    params = {"valid": ts}
    if sid != "":
        stationlimiter = " f.station = :sid and "
        params["sid"] = sid
        if sid.startswith("_"):
            # Magic here
            nt = NetworkTable("RAOB", only_online=False)
            ids = (
                nt.sts.get(sid, {})
                .get("name", f" -- {sid}")
                .split("--")[1]
                .strip()
                .split()
            )
            if len(ids) > 1:
                stationlimiter = " f.station = ANY(:sid) and "
                params["sid"] = ids
    pressurelimiter = ""
    if pressure > 0:
        pressurelimiter = " and p.pressure = :pid "
        params["pid"] = pressure
    with get_sqlalchemy_conn("raob") as conn:
        df = pd.read_sql(
            text(
                f"""
            SELECT f.station, p.pressure, p.height,
            round(p.tmpc::numeric,1) as tmpc,
            round(p.dwpc::numeric,1) as dwpc, p.drct,
            round((p.smps * 1.94384)::numeric,0) as sknt
            from raob_profile_{ts.year} p JOIN raob_flights f
                on (p.fid = f.fid)
            WHERE {stationlimiter} f.valid = :valid {pressurelimiter}
            ORDER by f.station, p.pressure DESC
            """
            ),
            conn,
            params=params,
            index_col=None,
        )
    for station, gdf in df.groupby("station"):
        profile = []
        for _, row in gdf.iterrows():
            profile.append(
                dict(
                    pres=safe(row["pressure"]),
                    hght=safe(row["height"]),
                    tmpc=safe(row["tmpc"]),
                    dwpc=safe(row["dwpc"]),
                    drct=safe(row["drct"]),
                    sknt=safe(row["sknt"]),
                )
            )
        res["profiles"].append(
            dict(
                station=station,
                valid=ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                profile=profile,
            )
        )
    return json.dumps(res)


def parse_time(tstring):
    """Allow for various timestamp formats"""
    if tstring is None or tstring == "":
        tstring = "201308211200"
    if tstring.find("T") > 0:
        # Assume ISO
        dt = datetime.datetime.strptime(tstring[:16], "%Y-%m-%dT%H:%M")
    else:
        dt = datetime.datetime.strptime(tstring[:12], "%Y%m%d%H%M")

    return dt.replace(tzinfo=ZoneInfo("UTC"))


@iemapp()
def application(environ, start_response):
    """Answer request."""
    sid = environ.get("station", "")[:4]
    if len(sid) == 3:
        sid = "K" + sid
    ts = parse_time(environ.get("ts"))
    pressure = int(environ.get("pressure", -1))
    cb = environ.get("callback")

    mckey = f"/json/raob/{ts:%Y%m%d%H%M}/{sid}/{pressure}?callback={cb}"
    mc = Client("iem-memcached:11211")
    data = mc.get(mckey)
    if data is not None:
        data = data.decode("utf-8")
    else:
        data = run(ts, sid, pressure)
        mc.set(mckey, data, 600)
    mc.close()

    if cb is not None:
        data = f"{html_escape(cb)}({data})"
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
