""".. title:: SPC/WPC Outlooks + coincident VTEC Events

Return to `API Services </api/>`_.

Documentation for /json/outlook_and_vtec.py
-------------------------------------------

This service emits the combination of SPC/WPC Outlooks and coincident VTEC
events.  This service is exploratory at the moment and may change as feedback
is received.  The spatial join is done against the storm based warning polygon.

Changelog
---------

- 2026-06-03: Initial release.

Example Usage
-------------

Provide the combination of Day 1 (8 UTC issuance)
Excessive Rainfall Outlook slight risks and
Flash Flood Warnings for NWS Des Moines.  Require that 5% of the Des Moines CWA
be covered by the given outlook to be considered.
Only include events during 2024.

https://mesonet.agron.iastate.edu/json/outlook_and_vtec.py?\
wfo=DMX&sdate=2024-01-01&edate=2024-12-31&day=1&overlap=5&threshold=SLGT&\
cycle=8&outlook_type=E&phsig=FF.W

"""

import json
import re
from datetime import date
from typing import Annotated

import pandas as pd
from pydantic import Field, field_validator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.nws.vtec import get_ps_string
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp

from iemweb.fields import (
    OUTLOOK_DAY_FIELD,
    WFO3_FIELD,
)
from iemweb.util import json_response_dict


class Schema(CGIModel):
    """See how we are called."""

    wfo: WFO3_FIELD
    day: OUTLOOK_DAY_FIELD = 1
    sdate: Annotated[
        date,
        Field(
            description="Inclusive outlook start date.",
            ge=date(2001, 1, 1),
        ),
    ]
    edate: Annotated[
        date,
        Field(
            description="Inclusive outlook end date.",
            ge=date(2001, 1, 1),
        ),
    ]
    overlap: Annotated[
        float,
        Field(
            description="Overlap minimum percentage for a WFO + ERO",
            ge=1,
            le=100,
        ),
    ] = 5
    threshold: Annotated[
        str,
        Field(
            description="Outlook threshold abbreviation",
        ),
    ] = "SLGT"
    cycle: Annotated[
        int,
        Field(
            description="Outlook issuance cycle",
            ge=0,
            le=23,
        ),
    ] = 8
    outlook_type: Annotated[
        str,
        Field(
            description=(
                "Outlook type. E for Excessive Rainfall, C for Convective, "
                "F for Fire Weather",
            ),
            pattern=r"^(E|C|F)$",
        ),
    ] = "E"
    phsig: Annotated[
        ListOrCSVType,
        Field(
            description=(
                "List of phenomena.significance to consider for the VTEC "
                "events.  For example, FF.W would be Flash Flood Warning."
            ),
            default_factory=lambda: ["FF.W"],
        ),
    ]

    @field_validator("phsig", mode="after")
    @classmethod
    def check_phsig(cls, v):
        """Convert from CSV if needed."""
        if isinstance(v, str):
            return [v]
        pattern = re.compile(r"^[A-Z]{2}\.[A-Z]$")
        for item in v:
            if not pattern.match(item):
                raise ValueError(f"Invalid phenomena.significance: {item}")
        return v


def do_query(query: Schema) -> dict:
    """Actually do stuff."""
    res = json_response_dict(
        {
            "outlooks": [],
            "stats": {},
        }
    )
    with get_sqlalchemy_conn("postgis") as conn:
        # OFFSET 0 hacks are for continued query planner pain
        dbentries = pd.read_sql(
            sql_helper("""
-- Candidate outlooks that spatially intersect the requested CWA
with pop as (
    select o.issue, o.expire, date(o.issue) as odate, geom, outlook_type,
    to_char(o.issue at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ') as utc_issue,
    to_char(o.expire at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ')
        as utc_expire, o.threshold, o.day, o.cycle
    from spc_outlooks o, cwa c where day = :day and cycle = :cycle and
    threshold = :threshold and outlook_date >= :sdate and
    outlook_date <= :edate and st_intersects(o.geom, c.the_geom)
    and c.cwa = :wfo and outlook_type = :outlook_type
    offset 0),

-- Compute the overlap percentage
candy as (
    select p.*,
    st_area(st_intersection(p.geom::geography, c.the_geom::geography)) /
    st_area(c.the_geom::geography) * 100. as overlap_percent
    from pop p, cwa c WHERE c.cwa = :wfo and
    st_area(st_intersection(p.geom::geography, c.the_geom::geography)) /
    st_area(c.the_geom::geography) * 100. >= :overlap),

-- Do the temporal join
warns as (
    select w.eventid, c.odate, c.overlap_percent, w.geom, w.vtec_year,
    w.phenomena, w.significance, w.wfo
    from sbw w, candy c WHERE w.status = 'NEW' and w.wfo = :wfo and
    w.phenomena || '.' || w.significance = Any(:phsig)
    and w.issue <= c.expire and w.expire > c.issue
    offset 0),

-- Again, we do a two step query due to planer issues
warns2 as (
    select f.eventid, f.vtec_year, p.odate, f.phenomena, f.significance,
    f.wfo, f.overlap_percent
    from warns f, pop p where
    f.odate = p.odate and st_intersects(f.geom, p.geom)
)
    -- Finally
    select p.odate, p.utc_issue, p.utc_expire, f.eventid, f.vtec_year,
    p.day, p.threshold, p.outlook_type, p.cycle, f.phenomena,
    f.significance, f.wfo, p.overlap_percent
    from candy p LEFT JOIN warns2 f on (p.odate = f.odate)
    order by odate, f.eventid asc
        """),
            conn,
            params={
                "wfo": query.wfo,
                "day": query.day,
                "cycle": query.cycle,
                "threshold": query.threshold,
                "sdate": query.sdate,
                "edate": query.edate,
                "overlap": query.overlap,
                "outlook_type": query.outlook_type,
                "phsig": query.phsig,
            },
        )
    for dt, gdf in dbentries.groupby("odate"):
        events = []
        for _, row in gdf[pd.notna(gdf["eventid"])].iterrows():
            pstr = get_ps_string(row["phenomena"], row["significance"])
            events.append(
                {
                    "eventid": int(row["eventid"]),
                    "vtec_year": row["vtec_year"],
                    "phenomena": row["phenomena"],
                    "significance": row["significance"],
                    "vtec_app_uri": (
                        f"/vtec/?wfo={row['wfo']}&eventid={row['eventid']:.0f}&"
                        f"year={row['vtec_year']:.0f}&phenomena={row['phenomena']}&"
                        f"significance={row['significance']}"
                    ),
                    "label": (f"{row['wfo']} {pstr} #{row['eventid']:.0f}"),
                }
            )
        row = gdf.iloc[0]
        res["outlooks"].append(
            {
                "date": dt.isoformat(),
                "overlap_percent": round(row["overlap_percent"], 2),
                "utc_issue": row["utc_issue"],
                "utc_expire": row["utc_expire"],
                "day": int(row["day"]),
                "threshold": row["threshold"],
                "outlook_type": row["outlook_type"],
                "cycle": int(row["cycle"]),
                "events": events,
            }
        )
    res["stats"]["total_outlooks"] = len(res["outlooks"])
    res["stats"]["outlooks_with_events"] = len(
        [x for x in res["outlooks"] if len(x["events"]) > 0]
    )
    return res


@iemapp(help=__doc__, schema=Schema)
def application(environ: dict, start_response: callable):
    """Answer request, iemapp decorator normalizes the response"""
    query: Schema = environ["_cgimodel_schema"]
    res = json.dumps(do_query(query))
    start_response("200 OK", [("Content-type", "application/json")])
    return res
