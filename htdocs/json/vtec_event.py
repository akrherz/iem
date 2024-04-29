"""VTEC event metadata"""

import datetime
import json

import httpx
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import LOG, html_escape
from pyiem.webutil import iemapp
from pymemcache.client import Client
from sqlalchemy import text


def run(wfo, year, phenomena, significance, etn):
    """Do great things"""
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
        "generation_time": datetime.datetime.utcnow().strftime(ISO8601),
        "year": year,
        "phenomena": phenomena,
        "significance": significance,
        "etn": etn,
        "wfo": wfo,
    }
    if df.empty:
        return json.dumps(res)

    # Get a list of unique product_ids
    product_ids = df["product_ids"].explode().dropna().unique()
    product_ids.sort()
    report = ""
    try:
        req = httpx.get(
            f"http://iem.local/api/1/nwstext/{product_ids[0]}", timeout=5
        )
        req.raise_for_status()
        report = req.text
    except Exception as exp:
        LOG.exception(exp)

    res["report"] = {"text": report}
    res["svs"] = []
    for product_id in product_ids[1:]:
        try:
            req = httpx.get(
                f"http://iem.local/api/1/nwstext/{product_id}", timeout=5
            )
            req.raise_for_status()
            res["svs"].append({"text": req.text})
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


@iemapp()
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

    phenomena = environ.get("phenomena", "SV")[:2]
    significance = environ.get("significance", "W")[:1]
    try:
        etn = int(environ.get("etn", 1))
    except ValueError:
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        data = "Invalid ETN"
        return [data.encode("ascii")]
    cb = environ.get("callback", None)

    mckey = f"/json/vtec_event/{wfo}/{year}/{phenomena}/{significance}/{etn}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = run(wfo, year, phenomena, significance, etn)
        mc.set(mckey, res, 300)
    else:
        res = res.decode("utf-8")
    mc.close()

    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("utf-8")]
