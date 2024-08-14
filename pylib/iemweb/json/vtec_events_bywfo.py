""".. title:: VTEC Events by WFO

Return to `API Services </api/#json>`_

Changelog
---------

- 2024-08-14: Initial documentation and pydantic validation

Example Requests
----------------

Return all Des Moines Tornado Warnings for 2024

https://mesonet.agron.iastate.edu/json/vtec_events_bywfo.py?\
wfo=DMX&year=2024&phenomena=TO&significance=W

Same request, csv format

https://mesonet.agron.iastate.edu/json/vtec_events_bywfo.py?\
wfo=DMX&year=2024&phenomena=TO&significance=W&fmt=csv

Same request, xlsx format

https://mesonet.agron.iastate.edu/json/vtec_events_bywfo.py?\
wfo=DMX&year=2024&phenomena=TO&significance=W&fmt=xlsx

"""

import json
from io import BytesIO, StringIO

import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(default=None, description="JSONP callback function")
    fmt: str = Field(
        default="json",
        description="The format of the response, either json or csv or xlsx",
        pattern="^(json|csv|xlsx)$",
    )
    start: AwareDatetime = Field(
        default=None,
        description="Start of period of interest",
    )
    end: AwareDatetime = Field(
        default=None,
        description="End of period of interest",
    )
    phenomena: str = Field(
        default=None,
        description="VTEC phenomena of interest",
        max_length=2,
    )
    significance: str = Field(
        default=None,
        description="VTEC significance of interest",
        max_length=1,
    )
    wfo: str = Field(
        default="DMX", description="3 character WFO identifier", max_length=3
    )
    year: int = Field(
        default=utc().year,
        ge=1986,
        le=utc().year,
        description="Year of interest",
    )


def make_url(row):
    """Build URL."""
    return (
        f"https://mesonet.agron.iastate.edu/vtec/#{row['vtec_year']}-"
        f"O-NEW-K{row['wfo']}-"
        f"{row['phenomena']}-{row['significance']}-{row['eventid']:04.0f}"
    )


def get_df(wfo, start, end, phenomena, significance):
    """Answer the request!"""
    params = {
        "wfo": wfo,
        "start": start,
        "end": end,
    }
    plimiter = ""
    if phenomena is not None:
        params["phenomena"] = phenomena
        plimiter = " and phenomena = :phenomena "
    if significance is not None:
        params["significance"] = significance
        plimiter += " and significance = :significance "
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
            SELECT
            to_char(product_issue at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as product_issued,
            to_char(init_expire at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as init_expired,
            to_char(issue at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as issued,
            to_char(expire at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as expired,
            to_char(updated at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as updated,
            to_char(purge_time at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as purge_time,
            eventid, phenomena, significance, hvtec_nwsli, wfo, ugc,
            product_ids[1] as product_id,
            vtec_year, product_ids[cardinality(product_ids)] as last_product_id
            from warnings WHERE wfo = :wfo and issue < :end
            and (expire > :start or init_expire > :start)
            {plimiter} ORDER by issue ASC
            """
            ),
            conn,
            params=params,
        )
    if df.empty:
        return df
    # Construct a URL
    df["url"] = df.apply(make_url, axis=1)
    return df


def as_json(df):
    """Materialize this df as JSON."""
    res = {"events": []}
    for _, row in df.iterrows():
        res["events"].append(
            {
                "url": row["url"],
                "product_issued": row["product_issued"],
                "issue": row["issued"],
                "expire": row["expired"],
                "init_expired": row["init_expired"],
                "purge_time": row["purge_time"],
                "updated": row["updated"],
                "eventid": row["eventid"],
                "phenomena": row["phenomena"],
                "hvtec_nwsli": row["hvtec_nwsli"],
                "significance": row["significance"],
                "last_product_id": row["last_product_id"],
                "product_id": row["product_id"],
                "wfo": row["wfo"],
                "ugc": row["ugc"],
            }
        )

    return json.dumps(res)


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Answer request."""
    wfo = environ["wfo"]
    year = environ["year"]
    start = environ["start"]
    end = environ["end"]
    if start is None or end is None:
        start = utc(year)
        end = utc(year + 1)
    phenomena = environ["phenomena"]
    significance = environ["significance"]
    fmt = environ["fmt"]

    df = get_df(wfo, start, end, phenomena, significance)
    if fmt == "xlsx":
        fn = f"vtec_{wfo}_{start:%Y%m%d%H%M}_{end:%Y%m%d%H%M}.xlsx"
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = f"vtec_{wfo}_{start:%Y%m%d%H%M}_{end:%Y%m%d%H%M}.csv"
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = StringIO()
        df.to_csv(bio, index=False)
        return [bio.getvalue().encode("utf-8")]

    res = as_json(df)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res.encode("ascii")
