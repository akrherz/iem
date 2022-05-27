"""Do a comparison with what's on SRH"""
from io import StringIO
import datetime

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn

SRH = "http://www.srh.noaa.gov/ridge2/shapefiles/psql_currenthazards.html"


def application(_environ, start_response):
    """Go Main Go"""
    sio = StringIO()
    start_response("200 OK", [("Content-type", "text/plain")])
    sio.write("Report run at %s\n" % (datetime.datetime.utcnow(),))
    try:
        srhdf = pd.read_html(SRH, header=0)[0]
    except Exception:
        sio.write("Failure to download %s, comparison failed" % (SRH,))
        return [sio.getvalue().encode("ascii")]
    srhdf["wfo"] = srhdf["wfo"].str.slice(1, 4)
    iemdf = read_sql(
        """
    SELECT wfo, phenomena, significance, eventid, count(*) from warnings
    where expire > now()
    GROUP by wfo, phenomena, significance, eventid
    """,
        get_dbconn("postgis"),
        index_col=["wfo", "phenomena", "significance", "eventid"],
    )
    for idx, g_srhdf in srhdf.groupby(["wfo", "phenom", "sig", "event"]):
        if idx not in iemdf.index:
            sio.write("IEM Missing %s\n" % (repr(idx),))
            continue
        if len(g_srhdf.index) != iemdf.at[idx, "count"]:
            sio.write(
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
            sio.write("SRH MISSING %s\n" % (repr(idx),))
    sio.write("DONE...\n")
    return [sio.getvalue().encode("ascii")]
