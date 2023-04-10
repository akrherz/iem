"""Do a comparison with what's on CRH CAP"""
import datetime
from io import StringIO

import requests
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn

# Akami has this cached, so we shall cache bust it, please
NOUNCE = "?%s" % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
URI = "https://www.weather.gov/source/crh/allhazard.geojson"


def application(_environ, start_response):
    """Go Main Go"""
    start_response("200 OK", [("Content-type", "text/plain")])
    sio = StringIO()
    sio.write("Report run at %s\n" % (datetime.datetime.utcnow(),))
    sio.write("Comparing %s\n" % (URI,))
    try:
        req = requests.get(URI + NOUNCE, timeout=30)
        jdata = req.json()
    except Exception as exp:
        sio.write(
            ("Failure to download %s, comparison failed\n" "%s") % (URI, exp)
        )
        return [sio.getvalue().encode("ascii")]
    sio.write(
        "geojson generation_time: %s\n" % (jdata.get("generation_time"),)
    )
    rows = []
    for feature in jdata["features"]:
        props = feature["properties"]
        for ugc in props.get("ugc", ["UNKNOW"]):
            rows.append(
                dict(
                    wfo=props["office"][1:],
                    ugc=ugc,
                    phenomena=props["phenom"],
                    significance=props["sig"],
                    eventid=int(props["etn"]),
                )
            )
    capdf = pd.DataFrame(rows)

    iemdf = read_sql(
        """
    SELECT ugc, wfo, phenomena, significance, eventid from warnings
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
            if len(row["phenomena"]) > 2:
                sio.write(
                    ("Indeteriminate %s %s %s %s %s\n")
                    % (
                        row["wfo"],
                        row["phenomena"],
                        row["significance"],
                        row["eventid"],
                        row["ugc"],
                    )
                )
                continue
            sio.write(
                ("IEM MISSING (%s %s %s %s %s)\n")
                % (
                    row["wfo"],
                    row["phenomena"],
                    row["significance"],
                    row["eventid"],
                    row["ugc"],
                )
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
                ("CRH MISSING (%s %s %s %s %s)\n")
                % (
                    row["wfo"],
                    row["phenomena"],
                    row["significance"],
                    row["eventid"],
                    row["ugc"],
                )
            )

    sio.write("DONE...\n")
    return [sio.getvalue().encode("ascii")]
