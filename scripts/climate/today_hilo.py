""" Generate a map of today's average high and low temperature"""
import datetime

import psycopg2.extras
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    today = datetime.date.today()
    now = today.replace(year=2000)
    nt = NetworkTable("IACLIMATE")
    nt.sts["IA0200"]["lon"] = -93.6
    nt.sts["IA5992"]["lat"] = 41.65
    coop = get_dbconn("coop")

    obs = []
    cursor = coop.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(
        "SELECT station, high, low from climate WHERE valid = %s "
        "and substr(station,0,3) = 'IA'",
        (now,),
    )
    for row in cursor:
        sid = row["station"]
        if sid[2] == "C" or sid[2:] == "0000" or sid not in nt.sts:
            continue
        obs.append(
            dict(
                id=sid[2:],
                lat=nt.sts[sid]["lat"],
                lon=nt.sts[sid]["lon"],
                tmpf=row["high"],
                dwpf=row["low"],
            )
        )

    mp = MapPlot(
        title=("Average High + Low Temperature [F] (1893-%s)") % (today.year,),
        subtitle="For Date: %s" % (now.strftime("%d %b"),),
        axisbg="white",
    )
    mp.drawcounties()
    mp.plot_station(obs)
    pqstr = (
        "plot ac %s0000 climate/iowa_today_avg_hilo_pt.png "
        "coop_avg_temp.png png"
    ) % (today.strftime("%Y%m%d"),)
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
