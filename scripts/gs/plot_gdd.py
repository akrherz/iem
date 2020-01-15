"""Generate a plot of GDD"""
import datetime

import numpy as np
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn

COOP = get_dbconn("coop")
ccursor = COOP.cursor()

nt = NetworkTable("IACLIMATE")


def run(base, ceil, now, fn):
    """ Generate the plot """
    # Compute normal from the climate database
    sql = """SELECT station,
       sum(gddxx(%s, %s, high, low)) as gdd
       from alldata_ia WHERE year = %s and month in (5,6,7,8,9,10)
       and station != 'IA0000' and substr(station,2,1) != 'C'
       GROUP by station""" % (
        base,
        ceil,
        now.year,
    )

    lats = []
    lons = []
    gdd50 = []
    ccursor.execute(sql)
    for row in ccursor:
        if row[0] not in nt.sts:
            continue
        lats.append(nt.sts[row[0]]["lat"])
        lons.append(nt.sts[row[0]]["lon"])
        gdd50.append(float(row[1]))

    mp = MapPlot(
        title=("Iowa 1 May - %s GDD Accumulation")
        % (now.strftime("%-d %B %Y"),),
        subtitle="base %s" % (base,),
    )
    bins = np.linspace(min(gdd50) - 1, max(gdd50) + 1, num=10, dtype=np.int)
    mp.contourf(lons, lats, gdd50, bins)
    mp.drawcounties()

    pqstr = "plot c 000000000000 summary/%s.png bogus png" % (fn,)
    mp.postprocess(pqstr=pqstr)


def main():
    """Main()"""
    today = datetime.datetime.now()
    if today.month < 5:
        today = today.replace(year=(today.year - 1), month=11, day=1)
    run(50, 86, today, "gdd_may1")
    run(60, 86, today, "gdd_may1_6086")
    run(65, 86, today, "gdd_may1_6586")


if __name__ == "__main__":
    main()
