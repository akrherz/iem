"""
Create a plot of today's estimated precipitation based on the MRMS data.

Called from RUN_10_AFTER.sh
"""

import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import click
import numpy as np
import pyiem.iemre as iemre
from pyiem.plot import MapPlot, nwsprecip
from pyiem.util import logger, mm2inch, ncopen, utc

LOG = logger()


def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    lts = utc(ts.year, ts.month, ts.day, 12)
    lts = lts.astimezone(ZoneInfo("America/Chicago"))
    # make assumptions about the last valid MRMS data
    if realtime:
        # Up until :59 after of the last hour
        lts = (datetime.now() - timedelta(hours=1)).replace(minute=59)
    else:
        lts = lts.replace(
            year=ts.year, month=ts.month, day=ts.day, hour=23, minute=59
        )

    idx = iemre.daily_offset(ts)
    ncfn = iemre.get_daily_mrms_ncname(ts.year)
    if not os.path.isfile(ncfn):
        LOG.info("File %s missing, abort.", ncfn)
        return
    with ncopen(ncfn, timeout=300) as nc:
        precip = nc.variables["p01d"][idx, :, :]
        lats = nc.variables["lat"][:]
        lons = nc.variables["lon"][:]
    subtitle = f"Total between 12:00 AM and {lts:%I:%M %p %Z}"
    routes = "ac"
    if not realtime:
        routes = "a"
    clevs = [
        0.01,
        0.1,
        0.25,
        0.5,
        0.75,
        1,
        1.5,
        2,
        2.5,
        3,
        3.5,
        4,
        5,
        6,
        8,
        10,
    ]

    (xx, yy) = np.meshgrid(lons, lats)
    for sector in ["iowa", "midwest"]:
        pqstr = (
            f"plot {routes} {ts:%Y%m%d%H}00 {sector}_q2_1d.png "
            f"{sector}_q2_1d.png png"
        )
        mp = MapPlot(
            title=f"{ts:%-d %b %Y} NCEP MRMS Today's Precipitation",
            subtitle=subtitle,
            sector=sector,
        )

        mp.pcolormesh(
            xx, yy, mm2inch(precip), clevs, cmap=nwsprecip(), units="inch"
        )
        if sector == "iowa":
            mp.drawcounties()
        mp.postprocess(pqstr=pqstr, view=False)
        mp.close()


@click.command()
@click.option("--date", "dt", required=True, type=click.DateTime())
def main(dt: datetime):
    """Main Method"""
    dt = dt.date()
    doday(dt, dt == date.today())


if __name__ == "__main__":
    main()
