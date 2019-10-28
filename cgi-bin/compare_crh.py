#!/usr/bin/env python
"""Do a comparison with what's on CRH CAP"""
from __future__ import print_function
import datetime

import requests
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, ssw

# Akami has this cached, so we shall cache bust it, please
NOUNCE = "?%s" % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
URI = "https://www.weather.gov/source/crh/allhazard.geojson"


def main():
    """Go Main Go"""
    ssw("Content-type: text/plain\n\n")
    ssw("Report run at %s\n" % (datetime.datetime.utcnow(),))
    ssw("Comparing %s\n" % (URI,))
    try:
        req = requests.get(URI + NOUNCE)
        jdata = req.json()
    except Exception as exp:
        ssw(("Failure to download %s, comparison failed\n" "%s") % (URI, exp))
        return
    ssw("geojson generation_time: %s\n" % (jdata.get("generation_time"),))
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
        get_dbconn("postgis", user="nobody"),
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
                print(
                    ("Indeteriminate %s %s %s %s %s")
                    % (
                        row["wfo"],
                        row["phenomena"],
                        row["significance"],
                        row["eventid"],
                        row["ugc"],
                    )
                )
                continue
            print(
                ("IEM MISSING (%s %s %s %s %s)")
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
            print(
                ("CRH MISSING (%s %s %s %s %s)")
                % (
                    row["wfo"],
                    row["phenomena"],
                    row["significance"],
                    row["eventid"],
                    row["ugc"],
                )
            )

    ssw("DONE...\n")


if __name__ == "__main__":
    main()
