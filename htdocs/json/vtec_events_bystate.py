"""Listing of VTEC events for state and year"""

import json
from io import BytesIO, StringIO

import pandas as pd
from pyiem.database import get_dbconnc
from pyiem.reference import ISO8601
from pyiem.util import html_escape
from pyiem.webutil import iemapp

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_res(state, year, phenomena, significance):
    """Generate a report of VTEC ETNs used for a WFO and year

    Args:
      wfo (str): 3 character WFO identifier
      year (int): year to run for
    """
    pgconn, cursor = get_dbconnc("postgis")

    limits = ["phenomena is not null", "significance is not null"]
    if phenomena != "__":
        limits[0] = f"phenomena = '{phenomena}'"
    if significance != "_":
        limits[1] = f"significance = '{significance}'"
    plimit = " and ".join(limits)
    cursor.execute(
        f"""
    WITH polyareas as (
        SELECT wfo, phenomena, significance, eventid, round((ST_area(
        ST_transform(geom,2163)) / 1000000.0)::numeric,0) as area
        from sbw_{year} s, states t WHERE
        ST_Overlaps(s.geom, t.the_geom) and
        t.state_abbr = %s and eventid is not null and {plimit}
        and status = 'NEW'
    ), ugcareas as (
        SELECT w.wfo,
        round(sum(ST_area(
            ST_transform(u.geom,2163)) / 1000000.0)::numeric,0) as area,
        string_agg(u.name || ' ['||u.state||']', ', ') as locations,
        eventid, phenomena, significance,
        min(issue) at time zone 'UTC' as utc_issue,
        max(expire) at time zone 'UTC' as utc_expire,
        min(product_issue) at time zone 'UTC' as utc_product_issue,
        max(init_expire) at time zone 'UTC' as utc_init_expire,
        max(hvtec_nwsli) as nwsli,
        max(fcster) as fcster from
        warnings_{year} w JOIN ugcs u on (w.gid = u.gid)
        WHERE substr(u.ugc, 1, 2) = %s and eventid is not null and {plimit}
        GROUP by w.wfo, phenomena, significance, eventid)

    SELECT u.*, coalesce(p.area, u.area) as myarea
    from ugcareas u LEFT JOIN polyareas p on
    (u.phenomena = p.phenomena and u.significance = p.significance
     and u.eventid = p.eventid and u.wfo = p.wfo)
        ORDER by u.phenomena ASC, u.significance ASC, u.utc_issue ASC
    """,
        (state, state),
    )
    res = {"state": state, "year": year, "events": []}
    for row in cursor:
        uri = "/vtec/#%s-O-NEW-K%s-%s-%s-%04i" % (
            year,
            row["wfo"],
            row["phenomena"],
            row["significance"],
            row["eventid"],
        )
        res["events"].append(
            dict(
                phenomena=row["phenomena"],
                significance=row["significance"],
                eventid=row["eventid"],
                hvtec_nwsli=row["nwsli"],
                area=float(row["myarea"]),
                locations=row["locations"],
                issue=row["utc_issue"].strftime(ISO8601),
                product_issue=row["utc_product_issue"].strftime(ISO8601),
                expire=row["utc_expire"].strftime(ISO8601),
                init_expire=row["utc_init_expire"].strftime(ISO8601),
                uri=uri,
                wfo=row["wfo"],
            )
        )
    pgconn.close()
    return res


@iemapp()
def application(environ, start_response):
    """Answer request."""
    state = environ.get("state", "IA")[:2]
    year = int(environ.get("year", 2015))
    phenomena = environ.get("phenomena", "__")[:2]
    significance = environ.get("significance", "_")[:1]
    cb = environ.get("callback")
    fmt = environ.get("fmt", "json")
    res = get_res(state, year, phenomena, significance)

    if fmt == "xlsx":
        fn = f"vtec_{state}_{year}_{phenomena}_{significance}.xlsx"
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        pd.DataFrame(res["events"]).to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = f"vtec_{state}_{year}_{phenomena}_{significance}.csv"
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = StringIO()
        pd.DataFrame(res["events"]).to_csv(bio, index=False)
        return [bio.getvalue().encode("utf-8")]

    res = json.dumps(res)
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
