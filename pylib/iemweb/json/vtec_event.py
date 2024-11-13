""".. title:: Metadata for a single VTEC event

Return to `API Services </api/#json>`_

Documentation for /json/vtec_event.py
-------------------------------------

This metadata service drives what is shown on the IEM's `VTEC Event </vtec/>`_
page.  This service requires that you already know the VTEC identifiers that
reference the event.  By default, this service attempts to bundle the raw NWS
text within the resulting JSON response.  This can be disabled by setting the
`include_text` parameter to something falsey.

Changelog
---------

- 2024-11-12: Added boolean attribute ``event_exists`` to the response to
  indicate if the event was found in the database.
- 2024-07-31: Initial documentation release and pydantic validation

Example Requests
----------------

Provide information about Des Moines Tornado Warning 110 during 2024.

https://mesonet.agron.iastate.edu/json/vtec_event.py\
?wfo=KDMX&phenomena=TO&significance=W&etn=110&year=2024

Provide information about Des Moines Tornado Warning 45 during 2024, but do
not include any text.

https://mesonet.agron.iastate.edu/json/vtec_event.py\
?wfo=KDMX&phenomena=TO&significance=W&etn=45&year=2024&include_text=0

"""

import json
from datetime import datetime

import httpx
import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import LOG, utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    include_text: bool = Field(
        default=True,
        description=(
            "Include the raw NWS text in the response, default is True"
        ),
    )
    wfo: str = Field(
        ...,
        description="Three character WFO identifier",
        min_length=3,
        max_length=4,
    )
    year: int = Field(
        ..., description="Year of the event", ge=1986, le=utc().year + 1
    )
    phenomena: str = Field(
        ..., description="VTEC Phenomena", min_length=2, max_length=2
    )
    significance: str = Field(
        ..., description="VTEC Significance", min_length=1, max_length=1
    )
    etn: int = Field(..., description="Event Tracking Number", ge=1, le=9999)


def run(environ):
    """Do great things"""
    wfo = environ["wfo"]
    if len(wfo) == 4:
        wfo = wfo[1:]

    phenomena = environ["phenomena"]
    significance = environ["significance"]
    etn = environ["etn"]
    year = environ["year"]

    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text("""
            select product_ids, name, status, hvtec_nwsli,
            product_issue at time zone 'UTC' as utc_product_issue,
            init_expire at time zone 'UTC' as utc_init_expire,
            updated at time zone 'UTC' as utc_updated,
            issue at time zone 'UTC' as utc_issue,
            expire at time zone 'UTC' as utc_expire,
            w.ugc from warnings w JOIN ugcs u on (w.gid = u.gid) where
            vtec_year = :year and w.wfo = :wfo and eventid = :etn and
            phenomena = :phenomena and significance = :significance
            """),
            conn,
            params={
                "year": year,
                "wfo": wfo,
                "etn": etn,
                "phenomena": phenomena,
                "significance": significance,
            },
        )

    res = {
        "generation_time": utc().strftime(ISO8601),
        "event_exists": not df.empty,
        "year": year,
        "phenomena": phenomena,
        "significance": significance,
        "etn": etn,
        "wfo": wfo,
        "report": {},
        "svs": [],
    }
    if df.empty:
        return json.dumps(res)

    # Get a list of unique product_ids
    product_ids = df["product_ids"].explode().dropna().unique().tolist()
    product_ids.sort()
    if product_ids:
        report = None
        valid = datetime.strptime(product_ids[0][:12], "%Y%m%d%H%M").strftime(
            ISO8601
        )
        if environ["include_text"]:
            try:
                resp = httpx.get(
                    f"http://iem.local/api/1/nwstext/{product_ids[0]}",
                    timeout=5,
                )
                resp.raise_for_status()
                report = resp.text
            except Exception as exp:
                LOG.exception(exp)

        res["report"] = {
            "text": report,
            "valid": valid,
            "product_id": product_ids[0],
        }
    for product_id in product_ids[1:]:
        try:
            valid = datetime.strptime(product_id[:12], "%Y%m%d%H%M").strftime(
                ISO8601
            )
            report = ""
            if environ["include_text"]:
                resp = httpx.get(
                    f"http://iem.local/api/1/nwstext/{product_id}", timeout=5
                )
                resp.raise_for_status()
                report = resp.text
            res["svs"].append(
                {"text": report, "valid": valid, "product_id": product_id}
            )
        except Exception as exp:
            LOG.exception(exp)

    res["utc_issue"] = df["utc_issue"].min().strftime(ISO8601)
    res["utc_expire"] = df["utc_expire"].max().strftime(ISO8601)

    res["ugcs"] = []
    for _, row in df.iterrows():
        res["ugcs"].append(
            {
                "ugc": row["ugc"],
                "name": row["name"],
                "status": row["status"],
                "hvtec_nwsli": row["hvtec_nwsli"],
                "utc_product_issue": row["utc_product_issue"].strftime(
                    ISO8601
                ),
                "utc_issue": row["utc_issue"].strftime(ISO8601),
                "utc_init_expire": row["utc_init_expire"].strftime(ISO8601),
                "utc_expire": row["utc_expire"].strftime(ISO8601),
                "utc_updated": row["utc_updated"].strftime(ISO8601),
            }
        )
    return json.dumps(res)


def get_mckey(environ: dict) -> str:
    """Compute the key."""
    return (
        f"/json/vtec_event/{environ['wfo']}/{environ['year']}/"
        f"{environ['phenomena']}/{environ['significance']}/{environ['etn']}/"
        f"{environ['include_text']}/v2"
    )


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey=get_mckey,
    memcacheexpire=300,
)
def application(environ, start_response):
    """Answer request."""
    res = run(environ)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res.encode("utf-8")
