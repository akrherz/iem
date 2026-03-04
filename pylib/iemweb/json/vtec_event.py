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

- 2026-02-26: Renamed top level metadata `generation_time` to `generated_at`
  for better IEM service consistency.
- 2024-11-12: Added boolean attribute ``event_exists`` to the response to
  indicate if the event was found in the database.
- 2024-07-31: Initial documentation release and pydantic validation

Example Requests
----------------

Provide information about NWS Des Moines Severe Thunderstorm Warning 110
during 2024.

https://mesonet.agron.iastate.edu/json/vtec_event.py\
?wfo=KDMX&phenomena=SV&significance=W&etn=110&year=2024

Provide information about NWS Des Moines Tornado Warning 45 during 2024, but do
not include any of the raw product text.

https://mesonet.agron.iastate.edu/json/vtec_event.py\
?wfo=KDMX&phenomena=TO&significance=W&etn=45&year=2024&include_text=0

"""

import json
from datetime import datetime

import httpx
import pandas as pd
from pydantic import Field, field_validator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.reference import ISO8601
from pyiem.util import LOG
from pyiem.webutil import CGIModel, iemapp

from iemweb.fields import (
    CALLBACK_FIELD,
    VTEC_PH_FIELD,
    VTEC_SIG_FIELD,
    VTEC_YEAR_FIELD,
)
from iemweb.mlib import unrectify_wfo
from iemweb.util import json_response_dict


class Schema(CGIModel):
    """See how we are called."""

    callback: CALLBACK_FIELD = None
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
        pattern=r"^[A-Z]{3,4}$",
    )
    year: VTEC_YEAR_FIELD
    phenomena: VTEC_PH_FIELD
    significance: VTEC_SIG_FIELD
    etn: int = Field(..., description="Event Tracking Number", ge=1, le=9999)

    @field_validator("wfo")
    @classmethod
    def validate_wfo(cls, v: str) -> str:
        """VTEC storage is 3 chars, so here we do the necessary evil."""
        return unrectify_wfo(v)


def run(environ: dict) -> str:
    """Do great things"""
    wfo = environ["wfo"]
    phenomena = environ["phenomena"]
    significance = environ["significance"]
    etn = environ["etn"]
    year = environ["year"]

    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            sql_helper("""
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

    res = json_response_dict(
        {
            "event_exists": not df.empty,
            "year": year,
            "phenomena": phenomena,
            "significance": significance,
            "etn": etn,
            "wfo": wfo,
            "report": {},
            "svs": [],
        }
    )
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
                # This request is outside this repo, so no need for internal
                # API routing
                resp = httpx.get(
                    (
                        "http://mesonet.agron.iastate.edu/"
                        f"api/1/nwstext/{product_ids[0]}"
                    ),
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
    memcacheexpire=15,  # Without cache invalidation, we have no choice
)
def application(environ, start_response):
    """Answer request."""
    res = run(environ)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res.encode("utf-8")
