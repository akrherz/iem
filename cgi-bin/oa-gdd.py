"""
 Produce a OA GDD Plot, dynamically!
"""
from io import BytesIO
import datetime

from paste.request import parse_formvars
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def application(environ, start_response):
    """Go Main Go"""
    pgconn = get_dbconn("coop")
    ccursor = pgconn.cursor()

    form = parse_formvars(environ)
    if (
        "year1" in form
        and "year2" in form
        and "month1" in form
        and "month2" in form
        and "day1" in form
        and "day2" in form
    ):
        sts = datetime.datetime(
            int(form["year1"]), int(form["month1"]), int(form["day1"])
        )
        ets = datetime.datetime(
            int(form["year2"]), int(form["month2"]), int(form["day2"])
        )
    else:
        sts = datetime.datetime(2011, 5, 1)
        ets = datetime.datetime(2011, 10, 1)
    baseV = 50
    if "base" in form:
        baseV = int(form["base"])
    maxV = 86
    if "max" in form:
        maxV = int(form["max"])

    # Make sure we aren't in the future
    now = datetime.datetime.today()
    if ets > now:
        ets = now

    st = NetworkTable("IACLIMATE")
    # Compute normal from the climate database
    sql = """
        SELECT station,
        sum(gddXX(%s, %s, high, low)) as gdd, count(*)
        from alldata_ia WHERE year = %s and day >= '%s' and day < '%s'
        and substr(station, 2, 1) != 'C' and station != 'IA0000'
        GROUP by station
    """ % (
        baseV,
        maxV,
        sts.year,
        sts.strftime("%Y-%m-%d"),
        ets.strftime("%Y-%m-%d"),
    )

    lats = []
    lons = []
    gdd50 = []
    valmask = []
    ccursor.execute(sql)
    total_days = (ets - sts).days
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

    m = MapPlot(
        title=("Iowa %s thru %s GDD(base=%s,max=%s) Accumulation" "")
        % (
            sts.strftime("%Y: %d %b"),
            (ets - datetime.timedelta(days=1)).strftime("%d %b"),
            baseV,
            maxV,
        ),
        axisbg="white",
    )
    m.contourf(lons, lats, gdd50, range(int(min(gdd50)), int(max(gdd50)), 25))
    m.plot_values(lons, lats, gdd50, fmt="%.0f")
    m.drawcounties()
    bio = BytesIO()
    m.fig.savefig(bio)
    m.close()
    start_response("200 OK", [("Content-type", "image/png")])
    return [bio.getvalue()]
