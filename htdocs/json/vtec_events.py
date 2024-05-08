"""Listing of VTEC events for a WFO and year"""

import datetime
import json
from io import BytesIO, StringIO

import pandas as pd
from pyiem.reference import ISO8601
from pyiem.util import html_escape, utc
from pyiem.webutil import iemapp

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_res(cursor, wfo, year, phenomena, significance, combo):
    """Generate a report of VTEC ETNs used for a WFO and year

    Args:
      wfo (str): 3 character WFO identifier
      year (int): year to run for
      phenomena (str, optional): 2 character phenomena
      significance (str, optional): 1 character VTEC significance
      combo (int, optional): special one-offs
    """
    limits = ["phenomena is not null", "significance is not null"]
    orderby = "u.phenomena ASC, u.significance ASC, u.utc_issue ASC"
    if phenomena != "":
        limits[0] = f"phenomena = '{phenomena}'"
    if significance != "":
        limits[1] = f"significance = '{significance}'"
    plimit = " and ".join(limits)
    if combo == 1:
        plimit = (
            "phenomena in ('SV', 'TO', 'FF', 'MA') and "
            "significance in ('W', 'A')"
        )
        orderby = "u.utc_issue ASC"
    cursor.execute(
        f"""
    WITH polyareas as (
        SELECT phenomena, significance, eventid, round((ST_area(
        ST_transform(geom,9311)) / 1000000.0)::numeric,0) as area
        from sbw WHERE vtec_year = %s and wfo = %s and eventid is not null and
        {plimit} and status = 'NEW'
    ), ugcareas as (
        SELECT
        round(sum(ST_area(
            ST_transform(u.geom,9311)) / 1000000.0)::numeric,0) as area,
        string_agg(u.name || ' ['||u.state||']', ', ') as locations,
        eventid, phenomena, significance,
        min(issue) at time zone 'UTC' as utc_issue,
        max(expire) at time zone 'UTC' as utc_expire,
        min(product_issue) at time zone 'UTC' as utc_product_issue,
        max(init_expire) at time zone 'UTC' as utc_init_expire,
        max(hvtec_nwsli) as nwsli,
        max(fcster) as fcster from warnings w JOIN ugcs u on (w.gid = u.gid)
        WHERE vtec_year = %s and w.wfo = %s and eventid is not null
        and {plimit}
        GROUP by phenomena, significance, eventid)

    SELECT u.*, coalesce(p.area, u.area) as myarea
    from ugcareas u LEFT JOIN polyareas p on
    (u.phenomena = p.phenomena and u.significance = p.significance
     and u.eventid = p.eventid) ORDER by {orderby}
    """,
        (year, wfo, year, wfo),
    )
    res = {
        "wfo": wfo,
        "generated_at": utc().strftime(ISO8601),
        "year": year,
        "events": [],
    }
    for row in cursor:
        uri = (
            f"/vtec/#{year}-O-NEW-K{wfo}-{row['phenomena']}-"
            f"{row['significance']}-{row['eventid']:04.0f}"
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
                url=f"https://mesonet.agron.iastate.edu{uri}",
                wfo=wfo,
                fcster=row["fcster"],
            )
        )
    return res


@iemapp(iemdb="postgis")
def application(environ, start_response):
    """Answer request."""
    wfo = environ.get("wfo", "MPX")
    if len(wfo) == 4:
        wfo = wfo[1:]
    try:
        year = int(environ.get("year", 2015))
    except ValueError:
        year = 0
    if year < 1986 or year > datetime.date.today().year + 1:
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        data = "Invalid Year"
        return [data.encode("ascii")]

    phenomena = environ.get("phenomena", "")[:2]
    significance = environ.get("significance", "")[:1]
    cb = environ.get("callback")
    combo = int(environ.get("combo", 0))

    fmt = environ.get("fmt", "json")
    res = get_res(
        environ["iemdb.postgis.cursor"],
        wfo,
        year,
        phenomena,
        significance,
        combo,
    )

    if fmt == "xlsx":
        fn = f"vtec_{wfo}_{year}_{phenomena}_{significance}.xlsx"
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        pd.DataFrame(res["events"]).to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = f"vtec_{wfo}_{year}_{phenomena}_{significance}.csv"
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
