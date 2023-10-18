"""
 Produce a OA GDD Plot, dynamically!
"""
import datetime
from io import BytesIO

from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn, utc
from pyiem.webutil import iemapp


@iemapp()
def application(environ, start_response):
    """Go Main Go"""
    pgconn = get_dbconn("coop")
    ccursor = pgconn.cursor()

    baseV = 50
    if "base" in environ:
        baseV = int(environ["base"])
    maxV = 86
    if "max" in environ:
        maxV = int(environ["max"])

    # Make sure we aren't in the future
    if "ets" not in environ:
        raise IncompleteWebRequest("Missing GET parameter ets=")
    ets = min(utc(), environ["ets"])

    st = NetworkTable("IACLIMATE")

    lats = []
    lons = []
    gdd50 = []
    valmask = []
    ccursor.execute(
        """
        SELECT station,
        sum(gddXX(%s, %s, high, low)) as gdd, count(*)
        from alldata_ia WHERE year = %s and day >= %s and day < %s
        and substr(station, 2, 1) != 'C' and station != 'IA0000'
        GROUP by station
    """,
        (
            baseV,
            maxV,
            environ["sts"].year,
            environ["sts"].strftime("%Y-%m-%d"),
            environ["ets"].strftime("%Y-%m-%d"),
        ),
    )
    total_days = (environ["ets"] - environ["sts"]).days
    for row in ccursor:
        sid = row[0]
        if sid not in st.sts:
            continue
        if row[2] < (total_days * 0.9):
            continue
        lats.append(st.sts[sid]["lat"])
        lons.append(st.sts[sid]["lon"])
        gdd50.append(float(row[1]))
        valmask.append(True)

    tt = (ets - datetime.timedelta(days=1)).strftime("%d %b")
    mp = MapPlot(
        title=(
            f"Iowa {environ['sts']:%Y: %d %b} thru {tt} "
            f"GDD(base={baseV},max={maxV}) Accumulation"
        ),
        axisbg="white",
    )
    mp.contourf(lons, lats, gdd50, range(int(min(gdd50)), int(max(gdd50)), 25))
    mp.plot_values(lons, lats, gdd50, fmt="%.0f")
    mp.drawcounties()
    bio = BytesIO()
    mp.fig.savefig(bio)
    mp.close()
    start_response("200 OK", [("Content-type", "image/png")])
    return [bio.getvalue()]
