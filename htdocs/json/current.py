"""Current Observation for a station and network"""
import json

from pyiem.reference import ISO8601
from pyiem.util import get_dbconnc, html_escape, utc
from pyiem.webutil import iemapp
from pymemcache.client import Client


def run(network, station):
    """Get last ob!"""
    pgconn, cursor = get_dbconnc("iem")
    cursor.execute(
        """
    WITH mystation as (SELECT * from stations where id = %s and network = %s),
    lastob as (select *, m.iemid as miemid,
        valid at time zone 'UTC' as utctime,
        valid at time zone m.tzname as localtime
        from current c JOIN mystation m on (c.iemid = m.iemid)),
    summ as (SELECT *, s.pday as s_pday from summary s JOIN lastob o
    on (s.iemid = o.miemid and s.day = date(o.localtime)))
    select * from summ
    """,
        (station, network),
    )
    if cursor.rowcount == 0:
        pgconn.close()
        return "{}"
    row = cursor.fetchone()
    pgconn.close()
    data = {}
    data["server_gentime"] = utc().strftime(ISO8601)
    data["id"] = station
    data["network"] = network
    ob = data.setdefault("last_ob", {})
    ob["local_valid"] = row["localtime"].strftime("%Y-%m-%d %H:%M")
    ob["utc_valid"] = row["utctime"].strftime(ISO8601)
    ob["airtemp[F]"] = row["tmpf"]
    ob["max_dayairtemp[F]"] = row["max_tmpf"]
    ob["min_dayairtemp[F]"] = row["min_tmpf"]
    ob["dewpointtemp[F]"] = row["dwpf"]
    ob["windspeed[kt]"] = row["sknt"]
    ob["winddirection[deg]"] = row["drct"]
    ob["altimeter[in]"] = row["alti"]
    ob["mslp[mb]"] = row["mslp"]
    ob["skycover[code]"] = [
        row["skyc1"],
        row["skyc2"],
        row["skyc3"],
        row["skyc4"],
    ]
    ob["skylevel[ft]"] = [
        row["skyl1"],
        row["skyl2"],
        row["skyl3"],
        row["skyl4"],
    ]
    ob["visibility[mile]"] = row["vsby"]
    ob["raw"] = row["raw"]
    ob["presentwx"] = [] if row["wxcodes"] is None else row["wxcodes"]
    ob["precip_today[in]"] = row["s_pday"]
    ob["c1tmpf[F]"] = row["c1tmpf"]
    ob["srad_1h[J m-2]"] = row["srad_1h_j"]
    for depth in [4, 8, 16, 20, 32, 40, 64, 128]:
        ob[f"tsoil[{depth}in][F]"] = row[f"tsoil_{depth}in_f"]
    return json.dumps(data)


@iemapp()
def application(environ, start_response):
    """Answer request."""
    network = environ.get("network", "IA_ASOS")[:32].upper()
    station = environ.get("station", "AMW")[:64].upper()
    cb = environ.get("callback", None)

    mckey = f"/json/current/{network}/{station}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = run(network, station)
        mc.set(mckey, res, 60)
    else:
        res = res.decode("utf-8")
    mc.close()

    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
