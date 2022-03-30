"""
 Create a plot of minimum wind chill
"""
import datetime
import sys

from pandas import read_sql
from pyiem.plot import MapPlot
from pyiem.util import get_dbconnstr
from pyiem.network import Table as NetworkTable


def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    nt = NetworkTable("IA_ASOS")
    df = read_sql(
        """
    SELECT id as station, min(feel) as wcht from current_log c JOIN stations t
    on (c.iemid = t.iemid) WHERE t.network = 'IA_ASOS'
    and valid >= %s and valid < %s + '24 hours'::interval
    and feel is not null and sknt > 0 GROUP by id
    """,
        get_dbconnstr("iem"),
        params=(ts, ts),
        index_col="station",
    )
    routes = "ac"
    if not realtime:
        routes = "a"
    lons = []
    lats = []
    vals = []
    labels = []
    for station, row in df.iterrows():
        lons.append(nt.sts[station]["lon"])
        lats.append(nt.sts[station]["lat"])
        vals.append(row["wcht"])
        labels.append(station)

    pqstr = (
        "plot %s %s00 summary/iowa_min_windchill.png "
        "summary/iowa_min_windchill.png png"
    ) % (routes, ts.strftime("%Y%m%d%H"))
    mp = MapPlot(
        title=(r"%s Minimum Wind Chill Temperature $^\circ$F")
        % (ts.strftime("%-d %b %Y"),),
        subtitle="Calm conditions are excluded from analysis",
        continentalcolor="white",
    )

    mp.plot_values(
        lons,
        lats,
        vals,
        "%.1f",
        labels=labels,
        textsize=12,
        labelbuffer=5,
        labeltextsize=10,
    )
    mp.drawcounties()
    mp.postprocess(pqstr=pqstr, view=False)
    mp.close()


def main():
    """Main Method"""
    if len(sys.argv) == 4:
        date = datetime.date(
            int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
        )
        realtime = False
    else:
        date = datetime.date.today()
        realtime = True
    doday(date, realtime)


if __name__ == "__main__":
    main()
