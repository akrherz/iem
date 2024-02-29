"""
Generate maps of Average Temperatures

called from climodat/run.sh
"""
import datetime
import sys

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot


def runYear(year):
    """Hack"""
    now = datetime.datetime.now()
    nt = NetworkTable("IACLIMATE")
    nt.sts["IA0200"]["lon"] = -93.4
    nt.sts["IA5992"]["lat"] = 41.65
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            SELECT station, avg(high) as avg_high, avg(low) as avg_low,
            avg( (high+low)/2 ) as avg_tmp, max(day)
            from alldata_ia WHERE year = %s and station != 'IA0000' and
            high is not Null and low is not Null and substr(station,3,1) != 'C'
            GROUP by station
            """,
            conn,
            params=(year,),
            index_col="station",
        )
    # Plot Average Highs
    lats = []
    lons = []
    vals = []
    labels = []
    for sid, row in df.iterrows():
        if sid not in nt.sts:
            continue
        labels.append(sid[2:])
        lats.append(nt.sts[sid]["lat"])
        lons.append(nt.sts[sid]["lon"])
        vals.append(row["avg_high"])
        maxday = row["max"]

    # ---------- Plot the points
    mp = MapPlot(
        title=f"Average Daily High Temperature [F] ({year})",
        subtitle="1 January - %s" % (maxday.strftime("%d %B"),),
        axisbg="white",
    )
    mp.plot_values(
        lons,
        lats,
        vals,
        labels=labels,
        labeltextsize=8,
        labelcolor="tan",
        fmt="%.1f",
    )
    pqstr = "plot m %s bogus %s/summary/avg_high.png png" % (
        now.strftime("%Y%m%d%H%M"),
        year,
    )
    mp.postprocess(pqstr=pqstr)
    mp.close()

    # Plot Average Lows
    lats = []
    lons = []
    vals = []
    labels = []
    for sid, row in df.iterrows():
        if sid not in nt.sts:
            continue
        labels.append(sid[2:])
        lats.append(nt.sts[sid]["lat"])
        lons.append(nt.sts[sid]["lon"])
        vals.append(row["avg_low"])

    # ---------- Plot the points
    mp = MapPlot(
        title="Average Daily Low Temperature [F] (%s)" % (year,),
        subtitle="1 January - %s" % (maxday.strftime("%d %B"),),
        axisbg="white",
    )
    mp.plot_values(
        lons,
        lats,
        vals,
        labels=labels,
        labeltextsize=8,
        labelcolor="tan",
        fmt="%.1f",
    )
    pqstr = "plot m %s bogus %s/summary/avg_low.png png" % (
        now.strftime("%Y%m%d%H%M"),
        year,
    )
    mp.postprocess(pqstr=pqstr)
    mp.close()

    # Plot Average Highs
    lats = []
    lons = []
    vals = []
    labels = []
    for sid, row in df.iterrows():
        if sid not in nt.sts:
            continue
        labels.append(sid[2:])
        lats.append(nt.sts[sid]["lat"])
        lons.append(nt.sts[sid]["lon"])
        vals.append(row["avg_tmp"])

    # ---------- Plot the points
    mp = MapPlot(
        title="Average Daily Temperature [F] (%s)" % (year,),
        subtitle="1 January - %s" % (maxday.strftime("%d %B"),),
        axisbg="white",
    )
    mp.plot_values(
        lons,
        lats,
        vals,
        labels=labels,
        labeltextsize=8,
        labelcolor="tan",
        fmt="%.1f",
    )
    pqstr = f"plot m {now:%Y%m%d%H%M} bogus {year}/summary/avg_temp.png png"
    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    runYear(sys.argv[1])
