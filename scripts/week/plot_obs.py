"""Plot 7 Day Precipitation Totals"""
import datetime
import sys

from pandas.io.sql import read_sql
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def fmter(val):
    """Make pretty text"""
    if val is None:
        return 0
    if val > 0 and val < 0.01:
        return "T"
    return "%.2f" % (val,)


def main(days, argv):
    """Go!"""
    today = datetime.date.today()
    routes = "ac"
    if len(argv) == 4:
        today = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
        routes = "a"
    sixago = today - datetime.timedelta(days=(days - 1))

    pgconn = get_dbconn("iem", user="nobody")

    # Compute normal from the climate database
    df = read_sql(
        """
        select s.id, ST_x(s.geom) as lon, ST_y(s.geom) as lat,
        sum(pday) as rainfall
        from summary c JOIN stations s on (c.iemid = s.iemid)
        WHERE day >= %s and day <= %s
        and s.network in ('AWOS', 'IA_ASOS')
        and pday >= 0 and pday < 30
        GROUP by s.id, lon, lat
    """,
        pgconn,
        params=(sixago, today),
        index_col="id",
    )
    df["label"] = df["rainfall"].apply(fmter)

    mp = MapPlot(
        title=("Iowa %s Day Precipitation Total [inch] (ASOS/AWOS)") % (days,),
        subtitle=("%s - %s inclusive")
        % (sixago.strftime("%d %b %Y"), today.strftime("%d %b %Y")),
        continentalcolor="white",
    )
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["label"].values,
        "%s",
        labels=df.index.values,
        labelbuffer=5,
    )
    mp.drawcounties()
    pqstr = (
        "plot %s %s0000 summary/%sday/ia_precip.png "
        "summary/%sday/ia_precip.png png"
    ) % (routes, today.strftime("%Y%m%d"), days, days)
    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    for _days in [7, 31, 91]:
        main(_days, sys.argv)
