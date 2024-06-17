"""
Produce a OA GDD Plot, dynamically!
"""

import datetime
from io import BytesIO

from pydantic import Field
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn, utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    base: int = Field(default=50, description="Base Temperature")
    max: int = Field(default=86, description="Max Temperature")
    sts: datetime.date = Field(None, description="Start Date")
    ets: datetime.date = Field(None, description="End Date")
    year1: int = Field(None, description="Year 1")
    year2: int = Field(None, description="Year 2")
    month1: int = Field(None, description="Month 1")
    month2: int = Field(None, description="Month 2")
    day1: int = Field(None, description="Day 1")
    day2: int = Field(None, description="Day 2")


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go Main Go"""
    pgconn = get_dbconn("coop")
    ccursor = pgconn.cursor()

    # Make sure we aren't in the future
    if environ["sts"] is None or environ["ets"] is None:
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
            environ["base"],
            environ["max"],
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
            f"GDD(base={environ['base']},max={environ['max']}) Accumulation"
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
