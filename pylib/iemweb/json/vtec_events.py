""".. title:: VTEC Events by WFO and Year

Return to `JSON Services </json/>`_

Documentation for /json/vtec_events.py
--------------------------------------

This provides metadata on VTEC events for a given WFO and year.

Changelog
---------

- 2024-08-08: Migration to pydantic validation

Example Usage
-------------

Provide all NWS Des Moines Tornado Warnings for 2024:

https://mesonet.agron.iastate.edu/json/vtec_events.py?wfo=DMX&year=2024\
&phenomena=TO&significance=W

Provide all SV, TO, FF, MA events for NWS Des Moines in 2024 in csv format:

https://mesonet.agron.iastate.edu/json/vtec_events.py?wfo=DMX&year=2024\
&combo=1&fmt=csv

Provide all 2024 tornado warnings for NWS Des Moines in xlsx format:

https://mesonet.agron.iastate.edu/json/vtec_events.py?wfo=DMX&year=2024\
&phenomena=TO&significance=W&fmt=xlsx

"""

import json
from io import BytesIO, StringIO

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import Connection, text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="optional JSONP callback")
    combo: bool = Field(
        default=False,
        description="Special one-off to get all SV, TO, FF, MA events",
    )
    fmt: str = Field(
        default="json",
        description="Output format, json, csv, xlsx",
        pattern="^(json|csv|xlsx)$",
    )
    phenomena: str = Field(
        default=None,
        description="2 character phenomena to limit results to",
        max_length=2,
    )
    significance: str = Field(
        default=None,
        description="1 character significance to limit results to",
        max_length=1,
    )
    wfo: str = Field(
        "MPX", description="3 character WFO identifier", max_length=4
    )
    year: int = Field(
        2015, description="Year to query", ge=1986, le=utc().year
    )


def get_res(conn: Connection, wfo, year, phenomena, significance, combo):
    """Generate a report of VTEC ETNs used for a WFO and year

    Args:
      wfo (str): 3 character WFO identifier
      year (int): year to run for
      phenomena (str, optional): 2 character phenomena
      significance (str, optional): 1 character VTEC significance
      combo (int, optional): special one-offs
    """
    params = {
        "year": year,
        "wfo": wfo,
        "phenomena": phenomena,
        "significance": significance,
    }
    limits = ["phenomena is not null", "significance is not null"]
    orderby = "u.phenomena ASC, u.significance ASC, u.utc_issue ASC"
    if phenomena is not None:
        limits[0] = "phenomena = :phenomena"
    if significance is not None:
        limits[1] = "significance = :significance"
    plimit = " and ".join(limits)
    if combo:
        plimit = (
            "phenomena in ('SV', 'TO', 'FF', 'MA') and "
            "significance in ('W', 'A')"
        )
        orderby = "u.utc_issue ASC"
    res = conn.execute(
        text(f"""
    WITH polyareas as (
        SELECT phenomena, significance, eventid, round((ST_area(
        ST_transform(geom,9311)) / 1000000.0)::numeric,0) as area
        from sbw WHERE vtec_year = :year and wfo = :wfo
        and eventid is not null and {plimit} and status = 'NEW'
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
        WHERE vtec_year = :year and w.wfo = :wfo and eventid is not null
        and {plimit}
        GROUP by phenomena, significance, eventid)

    SELECT u.*, coalesce(p.area, u.area) as myarea
    from ugcareas u LEFT JOIN polyareas p on
    (u.phenomena = p.phenomena and u.significance = p.significance
     and u.eventid = p.eventid) ORDER by {orderby}
    """),
        params,
    )
    data = {
        "wfo": wfo,
        "generated_at": utc().strftime(ISO8601),
        "year": year,
        "events": [],
    }
    for row in res.mappings():
        uri = (
            f"/vtec/#{year}-O-NEW-K{wfo}-{row['phenomena']}-"
            f"{row['significance']}-{row['eventid']:04.0f}"
        )
        data["events"].append(
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
    return data


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Answer request."""
    wfo = environ["wfo"]
    if len(wfo) == 4:
        wfo = wfo[1:]
    year = environ["year"]

    phenomena = environ["phenomena"]
    significance = environ["significance"]
    combo = environ["combo"]

    fmt = environ["fmt"]
    with get_sqlalchemy_conn("postgis") as pgconn:
        res = get_res(
            pgconn,
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

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res.encode("ascii")
