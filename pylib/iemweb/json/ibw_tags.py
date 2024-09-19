""".. title:: Impact Based Warning Tags by WFO and Year

Return to `API Services </api/#json>`_

Documentation for /json/ibw_tags.py
-----------------------------------

This service returns a JSON representation of Impact Based Warning Tags
(IBW) for a given year and WFO identifier.

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

DAMAGE_TAGS = "CONSIDERABLE DESTRUCTIVE CATASTROPHIC".split()
IEM = "https://mesonet.agron.iastate.edu"


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP Callback Name")
    damagetag: str = Field(None, description="Damage Tag", max_length=20)
    wfo: str = Field(None, description="WFO Identifier", max_length=4)
    year: int = Field(..., description="Year to query", ge=2000, le=utc().year)


def ptime(val):
    """Pretty print a timestamp"""
    if val is None:
        return val
    return val.strftime(ISO8601)


def run(wfo, damagetag, year):
    """Actually generate output"""
    params = {
        "wfo": wfo,
        "year": year,
    }
    wfolimiter = " w.wfo = :wfo and "
    damagelimiter = ""
    if damagetag is not None:
        damagetag = damagetag.upper()
        assert damagetag in DAMAGE_TAGS
        wfolimiter = ""
        params["damagetag"] = damagetag
        damagelimiter = (
            " (damagetag = :damagetag or floodtag_damage = :damagetag) and "
        )
    res = {
        "year": year,
        "wfo": wfo,
        "generated_at": utc().strftime(ISO8601),
        "gentime": utc().strftime(ISO8601),
        "results": [],
    }
    with get_sqlalchemy_conn("postgis") as conn:
        cursor = conn.execute(
            text(f"""
    WITH stormbased as (
     SELECT eventid, phenomena, issue at time zone 'UTC' as utc_issue,
     expire at time zone 'UTC' as utc_expire,
     polygon_begin at time zone 'UTC' as utc_polygon_begin,
     polygon_end at time zone 'UTC' as utc_polygon_end,
     status, windtag, hailtag, tornadotag, tml_sknt, damagetag, wfo,
     floodtag_flashflood, floodtag_damage, floodtag_heavyrain,
     floodtag_dam, floodtag_leeve, waterspouttag, product_id
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
 s.tornadotag, s.tml_sknt, s.damagetag, s.wfo, s.phenomena as ph,
 s.floodtag_flashflood, s.floodtag_damage, s.floodtag_heavyrain,
 s.floodtag_dam, s.floodtag_leeve, s.waterspouttag, product_id
 from countybased c JOIN stormbased s ON (c.eventid = s.eventid and
 c.phenomena = s.phenomena and c.wfo = s.wfo)
 ORDER by s.wfo ASC, eventid ASC, utc_polygon_begin ASC
     """),
            params,
        )

        for row in cursor.mappings():
            # TODO the wfo here is a bug without it being 4 char
            href = (
                f"{IEM}/vtec/#{year}-O-{row['status']}-K{row['wfo']}-"
                f"{row['ph']}-W-{row['eventid']:04.0f}"
            )
            data = dict(
                eventid=row["eventid"],
                locations=row["locations"],
                issue=ptime(row["utc_issue"]),
                expire=ptime(row["utc_expire"]),
                polygon_begin=ptime(row["utc_polygon_begin"]),
                polygon_end=ptime(row["utc_polygon_end"]),
                status=row["status"],
                windtag=row["windtag"],
                hailtag=row["hailtag"],
                tornadotag=row["tornadotag"],
                tml_sknt=row["tml_sknt"],
                damagetag=row["damagetag"],
                tornadodamagetag=row["damagetag"]
                if row["ph"] == "TO"
                else None,
                thunderstormdamagetag=row["damagetag"]
                if row["ph"] == "SV"
                else None,
                href=href,
                wfo=row["wfo"],
                phenomena=row["ph"],
                floodtag_flashflood=row["floodtag_flashflood"],
                floodtag_damage=row["floodtag_damage"],
                floodtag_heavyrain=row["floodtag_heavyrain"],
                floodtag_dam=row["floodtag_dam"],
                floodtag_leeve=row["floodtag_leeve"],
                waterspouttag=row["waterspouttag"],
                product_id=row["product_id"],
                product_href=f"{IEM}/p.php?pid={row['product_id']}",
                product_text=f"{IEM}/api/1/nwstext/{row['product_id']}",
            )
            res["results"].append(data)

    return json.dumps(res)


def get_mckey(environ):
    """ "Get the key."""
    damagetag = environ["damagetag"]
    year = environ["year"]
    wfo = environ["wfo"]
    return (
        f"/json/ibw_tags/{damagetag if damagetag is not None else wfo}/{year}"
    )


@iemapp(help=__doc__, schema=Schema, memcachekey=get_mckey)
def application(environ, start_response):
    """Answer request."""
    year = environ["year"]
    wfo = environ["wfo"]
    damagetag = environ["damagetag"]
    if wfo is None and damagetag is None:
        raise IncompleteWebRequest("wfo or damagetag is required")

    res = run(wfo, damagetag, year)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res
