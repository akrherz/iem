"""Generate a map of climatology.

Called from RUN_SUMMARY.sh
"""

from datetime import date

from pyiem.database import get_dbconnc
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot


def main():
    """Go Main Go"""
    today = date.today()
    now = today.replace(year=2000)
    nt = NetworkTable("IACLIMATE")
    nt.sts["IA0200"]["lon"] = -93.6
    nt.sts["IA5992"]["lat"] = 41.65
    pgconn, cursor = get_dbconnc("coop")

    obs = []
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
    pgconn.close()

    mp = MapPlot(
        title=f"Average High + Low Temperature [F] (1893-{today:%Y})",
        subtitle=f"For Date: {now:%-d %b}",
        axisbg="white",
    )
    mp.drawcounties()
    mp.plot_station(obs)
    pqstr = (
        f"plot ac {today:%Y%m%d}0000 climate/iowa_today_avg_hilo_pt.png "
        "coop_avg_temp.png png"
    )
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
