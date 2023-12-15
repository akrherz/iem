""" Service to dump out IBW tags for a WFO / Year"""
import datetime
import json

from pyiem.exceptions import NoDataFound
from pyiem.reference import ISO8601
from pyiem.util import get_dbconn, html_escape, utc
from pyiem.webutil import iemapp
from pymemcache.client import Client

DAMAGE_TAGS = "CONSIDERABLE DESTRUCTIVE CATASTROPHIC".split()


def ptime(val):
    """Pretty print a timestamp"""
    if val is None:
        return val
    return val.strftime(ISO8601)


def run(wfo, damagetag, year):
    """Actually generate output"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    wfolimiter = f" w.wfo = '{wfo}' and "
    damagelimiter = ""
    if damagetag is not None:
        damagetag = damagetag.upper()
        assert damagetag in DAMAGE_TAGS
        wfolimiter = ""
        damagelimiter = (
            f" (damagetag = '{damagetag}' or "
            f"floodtag_damage = '{damagetag}') and "
        )
    cursor.execute(
        f"""
    WITH stormbased as (
     SELECT eventid, phenomena, issue at time zone 'UTC' as utc_issue,
     expire at time zone 'UTC' as utc_expire,
     polygon_begin at time zone 'UTC' as utc_polygon_begin,
     polygon_end at time zone 'UTC' as utc_polygon_end,
     status, windtag, hailtag, tornadotag, tml_sknt, damagetag, wfo,
     floodtag_flashflood, floodtag_damage, floodtag_heavyrain,
     floodtag_dam, floodtag_leeve, waterspouttag
     from sbw_{year} w WHERE {damagelimiter} {wfolimiter}
     phenomena in ('SV', 'TO', 'FF', 'MA')
     and significance = 'W' and status != 'EXP' and status != 'CAN'
 ),

 countybased as (
     select string_agg( u.name || ' ['||u.state||']', ', ') as locations,
     eventid, phenomena, w.wfo from warnings_{year} w JOIN ugcs u
    ON (u.gid = w.gid) WHERE {wfolimiter}
    significance = 'W' and phenomena in ('SV', 'TO', 'FF', 'MA')
    and eventid is not null GROUP by w.wfo, eventid, phenomena
 )

 SELECT c.eventid, c.locations, s.utc_issue, s.utc_expire,
 s.utc_polygon_begin, s.utc_polygon_end, s.status, s.windtag, s.hailtag,
 s.tornadotag, s.tml_sknt, s.damagetag, s.wfo, s.phenomena,
 s.floodtag_flashflood, s.floodtag_damage, s.floodtag_heavyrain,
 s.floodtag_dam, s.floodtag_leeve, s.waterspouttag
 from countybased c JOIN stormbased s ON (c.eventid = s.eventid and
 c.phenomena = s.phenomena and c.wfo = s.wfo)
 ORDER by s.wfo ASC, eventid ASC, utc_polygon_begin ASC
     """,
    )

    res = dict(
        year=year,
        wfo=wfo,
        gentime=ptime(datetime.datetime.utcnow()),
        results=[],
    )
    for row in cursor:
        # TODO the wfo here is a bug without it being 4 char
        href = (
            f"/vtec/#{year}-O-{row[6]}-K{row[12]}-{row[13]}-W-{row[0]:04.0f}"
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
            waterspouttag=row[19],
        )
        res["results"].append(data)

    return json.dumps(res)


@iemapp()
def application(environ, start_response):
    """Answer request."""
    wfo = environ.get("wfo", "DMX")[:4]
    year = int(environ.get("year", 2015))
    if year < 2000 or year > utc().year:
        raise NoDataFound("Invalid year")
    damagetag = environ.get("damagetag")
    cb = environ.get("callback")

    mckey = (
        f"/json/ibw_tags/{damagetag if damagetag is not None else wfo}/{year}"
    )
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = run(wfo, damagetag, year)
        mc.set(mckey, res, 3600)
    else:
        res = res.decode("utf-8")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
