"""
Generate maps of Average Temperatures

called from climodat/run.sh
"""

from datetime import datetime

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot


@click.command()
@click.option("--year", type=int, help="Year to plot")
def main(year: int):
    """Hack"""
    now = datetime.now()
    nt = NetworkTable("IACLIMATE")
    nt.sts["IA0200"]["lon"] = -93.4
    nt.sts["IA5992"]["lat"] = 41.65
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
            SELECT station, avg(high) as avg_high, avg(low) as avg_low,
            avg( (high+low)/2 ) as avg_tmp, max(day)
            from alldata_ia WHERE year = :year and station != 'IA0000' and
            high is not Null and low is not Null and substr(station,3,1) != 'C'
            GROUP by station
            """),
            conn,
            params={"year": year},
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
        subtitle=f"1 January - {maxday:%d %B}",
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
    main()
