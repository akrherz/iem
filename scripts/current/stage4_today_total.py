"""
 Sum up the hourly precipitation from NCEP stage IV and produce maps
"""
import datetime
import os
import sys

import pygrib
from pyiem.datatypes import distance
from pyiem.plot import MapPlot, nwsprecip
from pyiem.util import logger
import pytz

LOG = logger()


def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day

    We should total files from 1 AM to midnight local time
    """
    sts = ts.replace(hour=1)
    ets = sts + datetime.timedelta(hours=24)
    interval = datetime.timedelta(hours=1)
    now = sts
    total = None
    lts = None
    while now < ets:
        gmt = now.astimezone(pytz.utc)
        fn = gmt.strftime(
            ("/mesonet/ARCHIVE/data/%Y/%m/%d/" "stage4/ST4.%Y%m%d%H.01h.grib")
        )
        if os.path.isfile(fn):
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
    lts = lts - datetime.timedelta(minutes=1)
    subtitle = "Total between 12:00 AM and %s" % (lts.strftime("%I:%M %p %Z"),)
    routes = "ac"
    if not realtime:
        routes = "a"
    for sector in ["iowa", "midwest", "conus"]:
        pqstr = ("plot %s %s00 %s_stage4_1d.png %s_stage4_1d.png png") % (
            routes,
            ts.strftime("%Y%m%d%H"),
            sector,
            sector,
        )

        mp = MapPlot(
            sector=sector,
            title=("%s NCEP Stage IV Today's Precipitation")
            % (ts.strftime("%-d %b %Y"),),
            subtitle=subtitle,
        )

        clevs = [0.01, 0.1, 0.3, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]
        mp.pcolormesh(
            lons,
            lats,
            distance(total, "MM").value("IN"),
            clevs,
            cmap=nwsprecip(),
            units="inch",
        )

        # map.drawstates(zorder=2)
        if sector == "iowa":
            mp.drawcounties()
        mp.postprocess(pqstr=pqstr)
        mp.close()


def main(argv):
    """ Go Main Go

    So the past hour's stage IV is available by about 50 after, so we should
    run for a day that is 90 minutes in the past by default

    """
    if len(argv) == 4:
        date = datetime.datetime(
            int(argv[1]), int(argv[2]), int(argv[3]), 12, 0
        )
        realtime = False
    else:
        date = datetime.datetime.now()
        date = date - datetime.timedelta(minutes=90)
        date = date.replace(hour=12, minute=0, second=0, microsecond=0)
        realtime = True
    # Stupid pytz timezone dance
    date = date.replace(tzinfo=pytz.utc)
    date = date.astimezone(pytz.timezone("America/Chicago"))
    doday(date, realtime)


if __name__ == "__main__":
    main(sys.argv)
