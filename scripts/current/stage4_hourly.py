"""
    Plot the hourly stage IV precip data
"""
import datetime
from zoneinfo import ZoneInfo

import click
import pygrib
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import archive_fetch, logger, mm2inch, utc

LOG = logger()


def doit(ts):
    """
    Generate hourly plot of stage4 data
    """
    gmtnow = utc()
    routes = "a"
    if ((gmtnow - ts).days * 86400.0 + (gmtnow - ts).seconds) < 7200:
        routes = "ac"

    ppath = f"{ts:%Y/%m/%d}/stage4/ST4.{ts:%Y%m%d%H}.01h.grib"
    with archive_fetch(ppath) as fn:
        if fn is None:
            LOG.info("Missing stage4 %s", ppath)
            return
        try:
            grbs = pygrib.open(fn)
            grib = grbs[1]
        except Exception:
            LOG.warning("Read %s failure", fn)
            return
        lats, lons = grib.latlons()
        vals = mm2inch(grib.values)

    cmap = get_cmap("jet")
    cmap.set_under("white")
    cmap.set_over("black")
    clevs = [
        0.01,
        0.05,
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.9,
        1,
        1.5,
        2,
        3,
    ]
    localtime = ts.astimezone(ZoneInfo("America/Chicago"))

    for sector in ["iowa", "midwest", "conus"]:
        mp = MapPlot(
            sector=sector,
            title="Stage IV One Hour Precipitation",
            subtitle="Hour Ending %s"
            % (localtime.strftime("%d %B %Y %I %p %Z"),),
        )
        mp.pcolormesh(lons, lats, vals, clevs, units="inch")
        pqstr = "plot %s %s00 %s_stage4_1h.png %s_stage4_1h_%s.png png" % (
            routes,
            ts.strftime("%Y%m%d%H"),
            sector,
            sector,
            ts.strftime("%H"),
        )
        if sector == "iowa":
            mp.drawcounties()
        mp.postprocess(view=False, pqstr=pqstr)
        mp.close()


@click.command()
@click.option("--valid", "ts", type=click.DateTime(), help="UTC Timestamp")
def main(ts):
    """Go main Go"""
    if ts is not None:
        ts = ts.replace(tzinfo=ZoneInfo("UTC"))
        doit(ts)
    else:
        ts = utc()
        doit(ts)
        doit(ts - datetime.timedelta(hours=24))
        doit(ts - datetime.timedelta(hours=48))


if __name__ == "__main__":
    main()
