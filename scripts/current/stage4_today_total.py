"""
Sum up the hourly precipitation from NCEP stage IV and produce maps

called from RUN_STAGE4.sh
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import click
import pygrib
from metpy.units import masked_array, units
from pyiem.plot import MapPlot, nwsprecip
from pyiem.util import archive_fetch, logger

LOG = logger()


def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day

    We should total files from 1 AM to midnight local time
    """
    LOG.info("Running for %s realtime: %s", ts, realtime)
    sts = ts.replace(hour=1)
    ets = sts + timedelta(hours=24)
    interval = timedelta(hours=1)
    now = sts
    total = None
    lts = None
    while now < ets:
        gmt = now.astimezone(ZoneInfo("UTC"))
        ppath = gmt.strftime("%Y/%m/%d/stage4/ST4.%Y%m%d%H.01h.grib")
        with archive_fetch(ppath) as fn:
            if fn is not None:
                lts = now
                grbs = pygrib.open(fn)
                if total is None:
                    total = grbs[1]["values"]
                    lats, lons = grbs[1].latlons()
                else:
                    total += grbs[1]["values"]
                grbs.close()
        now += interval

    if lts is None:
        if ts.hour > 1:
            LOG.info("found no data for date: %s", ts)
        return
    lts = lts - timedelta(minutes=1)
    subtitle = "Total between 12:00 AM and %s" % (lts.strftime("%I:%M %p %Z"),)
    routes = "ac"
    if not realtime:
        routes = "a"
    total = masked_array(total, units("mm")).to(units("inch")).m
    for sector in ["iowa", "midwest", "conus"]:
        pqstr = (
            f"plot {routes} {ts:%Y%m%d%H}00 {sector}_stage4_1d.png "
            f"{sector}_stage4_1d.png png"
        )

        mp = MapPlot(
            sector=sector,
            title=f"{ts:%-d %b %Y} NCEP Stage IV Today's Precipitation",
            subtitle=subtitle,
        )

        clevs = [0.01, 0.1, 0.3, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]
        mp.pcolormesh(lons, lats, total, clevs, cmap=nwsprecip(), units="inch")

        if sector == "iowa":
            mp.drawcounties()
        mp.postprocess(pqstr=pqstr)
        mp.close()


@click.command()
@click.option("--date", "dt", required=True, type=click.DateTime())
@click.option("--realtime", is_flag=True, default=False)
def main(dt: datetime, realtime: bool):
    """Go Main Go

    So the past hour's stage IV is available by about 50 after, so we should
    run for a day that is 90 minutes in the past by default

    """
    dt = dt.replace(hour=12, tzinfo=ZoneInfo("America/Chicago"))
    doday(dt, realtime)


if __name__ == "__main__":
    main()
