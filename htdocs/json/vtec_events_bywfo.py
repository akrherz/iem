"""Pidgin-holed service for some WFO data..."""

import datetime
import json
from io import BytesIO, StringIO

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import html_escape
from pyiem.webutil import iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


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


@iemapp()
def application(environ, start_response):
    """Answer request."""
    wfo = environ.get("wfo", "DMX")[:3].upper()
    year = int(environ.get("year", datetime.date.today().year))
    start = datetime.datetime.strptime(
        environ.get("start", f"{year}-01-01T00:00")[:16], "%Y-%m-%dT%H:%M"
    ).replace(tzinfo=datetime.timezone.utc)
    end = datetime.datetime.strptime(
        environ.get("end", f"{year}-12-31T23:59")[:16], "%Y-%m-%dT%H:%M"
    ).replace(tzinfo=datetime.timezone.utc)
    phenomena = environ.get("phenomena")
    significance = environ.get("significance")
    cb = environ.get("callback", None)
    fmt = environ.get("fmt", "json")

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
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
