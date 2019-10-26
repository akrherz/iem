#!/usr/bin/env python
"""Do a comparison with what's on SRH"""
from __future__ import print_function
import datetime

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, ssw

SRH = "http://www.srh.noaa.gov/ridge2/shapefiles/psql_currenthazards.html"


def main():
    """Go Main Go"""
    ssw("Content-type: text/plain\n\n")
    ssw("Report run at %s\n" % (datetime.datetime.utcnow(),))
    try:
        srhdf = pd.read_html(SRH, header=0)[0]
    except Exception:
        ssw("Failure to download %s, comparison failed" % (SRH,))
        return
    srhdf["wfo"] = srhdf["wfo"].str.slice(1, 4)
    iemdf = read_sql(
        """
    SELECT wfo, phenomena, significance, eventid, count(*) from warnings
    where expire > now()
    GROUP by wfo, phenomena, significance, eventid
    """,
        get_dbconn("postgis", user="nobody"),
        index_col=["wfo", "phenomena", "significance", "eventid"],
    )
    for idx, g_srhdf in srhdf.groupby(["wfo", "phenom", "sig", "event"]):
        if idx not in iemdf.index:
            ssw("IEM Missing %s\n" % (repr(idx),))
            continue
        if len(g_srhdf.index) != iemdf.at[idx, "count"]:
            ssw(
                ("%s Count Mismatch IEM: %s SRH: %s\n")
                % (repr(idx), iemdf.at[idx, "count"], len(g_srhdf.index))
            )
    for idx, _row in iemdf.iterrows():
        (wfo, phenomena, significance, eventid) = idx
        df2 = srhdf[
            (
                (srhdf["phenom"] == phenomena)
                & (srhdf["sig"] == significance)
                & (srhdf["event"] == eventid)
                & (srhdf["wfo"] == wfo)
            )
        ]
        if df2.empty:
            ssw("SRH MISSING %s\n" % (repr(idx),))
    ssw("DONE...\n")


if __name__ == "__main__":
    main()
