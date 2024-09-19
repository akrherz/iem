""".. title:: VTEC Events by State and Year

Return to `JSON Services </json/>`_

Changelog
---------

- 2024-08-14: Initital documentation update and pydantic validation

Example Requests
----------------

Get all Iowa events for 2024 in JSON, then CSV, then XLSX format.

https://mesonet.agron.iastate.edu/json/vtec_events_bystate.py\
?state=IA&year=2024

https://mesonet.agron.iastate.edu/json/vtec_events_bystate.py\
?state=IA&year=2024&fmt=csv

https://mesonet.agron.iastate.edu/json/vtec_events_bystate.py\
?state=IA&year=2024&fmt=xlsx

Get all Tornado Warnings for Iowa during 2024.

https://mesonet.agron.iastate.edu/json/vtec_events_bystate.py\
?state=IA&year=2024&phenomena=TO&significance=W

"""

import json
from io import BytesIO, StringIO

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(default=None, description="optional JSONP callback")
    fmt: str = Field(
        default="json",
        description="The format of the response, json, csv, or xlsx",
        pattern="^(json|csv|xlsx)$",
    )
    phenomena: str = Field(
        default="__",
        description="2 character phenomena identifier",
        max_length=2,
    )
    significance: str = Field(
        default="_",
        description="1 character significance identifier",
        max_length=1,
    )
    state: str = Field(
        default=..., description="2 character state identifier", max_length=2
    )
    year: int = Field(
        default=...,
        description="Year to query for",
        ge=1986,
        le=utc().year,
    )


def get_res(state, year, phenomena, significance):
    """Generate a report of VTEC ETNs used for a WFO and year

    Args:
      wfo (str): 3 character WFO identifier
      year (int): year to run for
    """

    limits = ["phenomena is not null", "significance is not null"]
    if phenomena != "__":
        limits[0] = "phenomena = :ph"
    if significance != "_":
        limits[1] = "significance = :sig"
    plimit = " and ".join(limits)
    data = {"state": state, "year": year, "events": []}
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text(f"""
    WITH polyareas as (
        SELECT wfo, phenomena, significance, eventid, round((ST_area(
        ST_transform(geom,9311)) / 1000000.0)::numeric,0) as area
        from sbw s, states t WHERE
        vtec_year = :year and ST_Overlaps(s.geom, t.the_geom) and
        t.state_abbr = :st and eventid is not null and {plimit}
        and status = 'NEW'
    ), ugcareas as (
        SELECT w.wfo,
        round(sum(ST_area(
            ST_transform(u.geom,9311)) / 1000000.0)::numeric,0) as area,
        string_agg(u.name || ' ['||u.state||']', ', ') as locations,
        eventid, phenomena, significance,
        min(issue) at time zone 'UTC' as utc_issue,
        max(expire) at time zone 'UTC' as utc_expire,
        min(product_issue) at time zone 'UTC' as utc_product_issue,
        max(init_expire) at time zone 'UTC' as utc_init_expire,
        max(hvtec_nwsli) as nwsli,
        max(fcster) as fcster from
        warnings w JOIN ugcs u on (w.gid = u.gid)
        WHERE vtec_year = :year and substr(u.ugc, 1, 2) = :st
        and eventid is not null and {plimit}
        GROUP by w.wfo, phenomena, significance, eventid)

    SELECT u.*, coalesce(p.area, u.area) as myarea
    from ugcareas u LEFT JOIN polyareas p on
    (u.phenomena = p.phenomena and u.significance = p.significance
     and u.eventid = p.eventid and u.wfo = p.wfo)
        ORDER by u.phenomena ASC, u.significance ASC, u.utc_issue ASC
    """),
            {"year": year, "st": state, "ph": phenomena, "sig": significance},
        )
        for row in res.mappings():
            uri = (
                f"/vtec/#{year}-O-NEW-K{row['wfo']}-{row['phenomena']}-"
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
                    wfo=row["wfo"],
                )
            )
    return data


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Answer request."""
    state = environ["state"]
    year = environ["year"]
    phenomena = environ["phenomena"]
    significance = environ["significance"]
    fmt = environ["fmt"]
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

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res.encode("ascii")
