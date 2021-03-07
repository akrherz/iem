""" Service to dump out IBW tags for a WFO / Year"""
import json
import datetime

import memcache
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape


def ptime(val):
    """Pretty print a timestamp"""
    if val is None:
        return val
    return val.strftime("%Y-%m-%dT%H:%M:%SZ")


def run(wfo, year):
    """ Actually generate output """
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        """
    WITH stormbased as (
     SELECT eventid, phenomena, issue at time zone 'UTC' as utc_issue,
     expire at time zone 'UTC' as utc_expire,
     polygon_begin at time zone 'UTC' as utc_polygon_begin,
     polygon_end at time zone 'UTC' as utc_polygon_end,
     status, windtag, hailtag, tornadotag, tml_sknt, damagetag, wfo,
     floodtag_flashflood, floodtag_damage, floodtag_heavyrain,
     floodtag_dam, floodtag_leeve
     from sbw_"""
        + str(year)
        + """ WHERE wfo = %s
     and phenomena in ('SV', 'TO', 'FF', 'MA')
     and significance = 'W' and status != 'EXP' and status != 'CAN'
 ),

 countybased as (
     select string_agg( u.name || ' ['||u.state||']', ', ') as locations,
     eventid, phenomena from warnings_"""
        + str(year)
        + """ w JOIN ugcs u
    ON (u.gid = w.gid) WHERE w.wfo = %s and
    significance = 'W' and phenomena in ('SV', 'TO', 'FF', 'MA')
    and eventid is not null GROUP by eventid, phenomena
 )

 SELECT c.eventid, c.locations, s.utc_issue, s.utc_expire,
 s.utc_polygon_begin, s.utc_polygon_end, s.status, s.windtag, s.hailtag,
 s.tornadotag, s.tml_sknt, s.damagetag, s.wfo, s.phenomena,
 s.floodtag_flashflood, s.floodtag_damage, s.floodtag_heavyrain,
 s.floodtag_dam, s.floodtag_leeve
 from countybased c, stormbased s WHERE c.eventid = s.eventid and
 c.phenomena = s.phenomena
 ORDER by eventid ASC, utc_polygon_begin ASC
     """,
        (wfo, wfo),
    )

    res = dict(
        year=year,
        wfo=wfo,
        gentime=ptime(datetime.datetime.utcnow()),
        results=[],
    )
    for row in cursor:
        # TODO the wfo here is a bug without it being 4 char
        href = "/vtec/#%s-O-%s-K%s-%s-W-%04i" % (
            year,
            row[6],
            row[12],
            row[13],
            row[0],
        )
        data = dict(
            eventid=row[0],
            locations=row[1],
            issue=ptime(row[2]),
            expire=ptime(row[3]),
            polygon_begin=ptime(row[4]),
            polygon_end=ptime(row[5]),
            status=row[6],
            windtag=row[7],
            hailtag=row[8],
            tornadotag=row[9],
            tml_sknt=row[10],
            damagetag=row[11],
            tornadodamagetag=row[11] if row[13] == "TO" else None,
            thunderstormdamagetag=row[11] if row[13] == "SV" else None,
            href=href,
            wfo=row[12],
            phenomena=row[13],
            floodtag_flashflood=row[14],
            floodtag_damage=row[15],
            floodtag_heavyrain=row[16],
            floodtag_dam=row[17],
            floodtag_leeve=row[18],
        )
        res["results"].append(data)

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    wfo = fields.get("wfo", "DMX")[:4]
    year = int(fields.get("year", 2015))
    cb = fields.get("callback")

    mckey = "/json/ibw_tags/v2/%s/%s" % (wfo, year)
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(wfo, year)
        mc.set(mckey, res, 3600)

    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
