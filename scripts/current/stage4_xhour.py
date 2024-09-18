"""
Create a variable X hour plot of stage IV estimates

Called from RUN_STAGE4.sh
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import click
import pygrib
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import archive_fetch, logger, mm2inch

LOG = logger()


def do(ts: datetime, hours: int, realtime: bool):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    ts = ts.replace(minute=0)
    sts = ts - timedelta(hours=hours)
    ets = ts
    interval = timedelta(hours=1)
    now = sts
    total = None
    lts = None
    while now < ets:
        ppath = f"{now:%Y/%m/%d}/stage4/ST4.{now:%Y%m%d%H}.01h.grib"
        with archive_fetch(ppath) as fn:
            if fn is not None:
                lts = now
                with pygrib.open(fn) as grbs:
                    if total is None:
                        g = grbs[1]
                        total = g["values"].filled(0)
                        lats, lons = g.latlons()
                    else:
                        total += grbs[1]["values"].filled(0)
        now += interval

    if lts is None and ts.hour > 1:
        LOG.info("Missing StageIV data!")
    if lts is None:
        return

    cmap = get_cmap("jet")
    cmap.set_under("white")
    cmap.set_over("black")
    clevs = [0.01, 0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 9.9]
    localtime = (ts - timedelta(minutes=1)).astimezone(
        ZoneInfo("America/Chicago")
    )

    for sector in ["iowa", "midwest", "conus"]:
        mp = MapPlot(
            sector=sector,
            title=f"NCEP Stage IV {hours} Hour Precipitation",
            subtitle=f"Total up to {localtime:%d %B %Y %I %p %Z}",
        )
        mp.pcolormesh(lons, lats, mm2inch(total), clevs, units="inch")
        pqstr = (
            f"plot {'ac' if realtime else 'a'} {ts:%Y%m%d%H}00 "
            f"{sector}_stage4_{hours}h.png "
            f"{sector}_stage4_{hours}h_{ts:%H}.png png"
        )
        if sector == "iowa":
            mp.drawcounties()
        LOG.info("Sending %s", pqstr)
        mp.postprocess(pqstr=pqstr)
        mp.close()


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
@click.option("--hours", type=int, required=True)
@click.option("--realtime", is_flag=True, default=False)
def main(valid: datetime, hours: int, realtime: bool):
    """Go Main Go"""
    valid = valid.replace(tzinfo=ZoneInfo("UTC"))
    do(valid, hours, realtime)


if __name__ == "__main__":
    main()
