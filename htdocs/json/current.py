#!/usr/bin/env python
"""Current Observation for a station and network"""
import json
import datetime

import memcache
import psycopg2.extras
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape


def run(network, station):
    """Get last ob!"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(
        """
    WITH mystation as (SELECT * from stations where id = %s and network = %s),
    lastob as (select *, m.iemid as miemid,
        valid at time zone 'UTC' as utctime,
        valid at time zone m.tzname as localtime
        from current c JOIN mystation m on (c.iemid = m.iemid)),
    summ as (SELECT * from summary s JOIN lastob o on (s.iemid = o.miemid and
    s.day = date(o.localtime)))
    select * from summ
    """,
        (station, network),
    )
    if cursor.rowcount == 0:
        return "{}"
    row = cursor.fetchone()
    data = dict()
    data["server_gentime"] = datetime.datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    data["id"] = station
    data["network"] = network
    ob = data.setdefault("last_ob", dict())
    ob["local_valid"] = row["localtime"].strftime("%Y-%m-%d %H:%M")
    ob["utc_valid"] = row["utctime"].strftime("%Y-%m-%dT%H:%M:00Z")
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
    return json.dumps(data)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    network = fields.get("network", "IA_ASOS")[:10].upper()
    station = fields.get("station", "AMW")[:10].upper()
    cb = fields.get("callback", None)

    mckey = "/json/current/%s/%s" % (network, station)
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(network, station)
        mc.set(mckey, res, 60)

    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
