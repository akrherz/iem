#!/usr/bin/env python
"""Do a comparison with what's on api.weather.gov/cap"""
from io import StringIO

import pandas as pd
import requests
import simplejson
from pandas.io.sql import read_sql
from pyiem.nws.vtec import parse as vtec_parse
from pyiem.util import get_dbconn, utc

CAP = "https://api.weather.gov/alerts/active"


def application(_environ, start_response):
    """Go Main Go"""
    sio = StringIO()
    start_response("200 OK", [("Content-type", "text/plain")])
    sio.write(f"Report run at {utc():%Y-%m-%dT%H:%M:%SZ}\n")
    sio.write(f"Comparison against {CAP}\n")
    try:
        req = requests.get(
            CAP, headers={"Accept": "application/geo+json"}, timeout=30
        )
        if req.status_code != 200:
            sio.write(f"Download failed with status_code {req.status_code}")
        jdata = req.json()
    except requests.exceptions.BaseHTTPError as exp:
        sio.write(f"Failure to download {CAP}, comparison failed {exp}\n")
        return None
    except simplejson.errors.JSONDecodeError as exp:
        sio.write(f"Download {CAP} had bad JSON {req.content} {exp}\n")
        return None
    rows = []
    for feature in jdata["features"]:
        props = feature["properties"]
        vtecstring = props.get("parameters", {}).get("VTEC")
        if vtecstring is None:
            continue
        vtec = vtec_parse(vtecstring[0])[0]
        for ugc in props["geocode"]["UGC"]:
            rows.append(
                dict(
                    wfo=vtec.office,
                    phenomena=vtec.phenomena,
                    significance=vtec.significance,
                    eventid=vtec.etn,
                    ugc=ugc,
                )
            )
    capdf = pd.DataFrame(rows)

    iemdf = read_sql(
        """
    SELECT wfo, phenomena, significance, eventid, ugc from warnings
    where expire > now()
    """,
        get_dbconn("postgis"),
        index_col=None,
    )
    for _idx, row in capdf.iterrows():
        df2 = iemdf[
            (
                (iemdf["phenomena"] == row["phenomena"])
                & (iemdf["significance"] == row["significance"])
                & (iemdf["eventid"] == row["eventid"])
                & (iemdf["wfo"] == row["wfo"])
                & (iemdf["ugc"] == row["ugc"])
            )
        ]
        if df2.empty:
            sio.write(
                f"IEM MISSING ({row['wfo']} {row['phenomena']} "
                f"{row['significance']} {row['eventid']} {row['ugc']})\n"
            )

    for _idx, row in iemdf.iterrows():
        df2 = capdf[
            (
                (capdf["phenomena"] == row["phenomena"])
                & (capdf["significance"] == row["significance"])
                & (capdf["eventid"] == row["eventid"])
                & (capdf["wfo"] == row["wfo"])
                & (capdf["ugc"] == row["ugc"])
            )
        ]
        if df2.empty:
            sio.write(
                f"NWS MISSING ({row['wfo']} {row['phenomena']} "
                f"{row['significance']} {row['eventid']} {row['ugc']})\n"
            )

    sio.write("DONE...\n")
    return [sio.getvalue().encode("ascii")]
