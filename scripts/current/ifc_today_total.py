"""
Create a plot of today's IFC estimated precip
"""

from datetime import datetime, timedelta

import click
import numpy as np
from pyiem.iemre import daily_offset
from pyiem.plot import MapPlot, nwsprecip
from pyiem.util import mm2inch, ncopen


def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    idx = daily_offset(ts)
    with ncopen(
        f"/mesonet/data/iemre/{ts.year}_ifc_daily.nc", timeout=300
    ) as nc:
        xaxis = nc.variables["lon"][:]
        yaxis = nc.variables["lat"][:]
        total = nc.variables["p01d"][idx, :, :]
    lastts = datetime(ts.year, ts.month, ts.day, 23, 59)
    if realtime:
        now = datetime.now() - timedelta(minutes=60)
        lastts = now.replace(minute=59)
    subtitle = f"Total between 12:00 AM and {lastts:%I:%M %p}"
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

    pqstr = (
        f"plot {routes} {ts:%Y%m%d%H}00 iowa_ifc_1d.png iowa_ifc_1d.png png"
    )
    mp = MapPlot(
        title=f"{ts:%-d %b %Y} Iowa Flood Center Today's Precipitation",
        subtitle=subtitle,
        sector="custom",
        west=xaxis[0],
        east=xaxis[-1],
        south=yaxis[0],
        north=yaxis[-1],
    )

    (lons, lats) = np.meshgrid(xaxis, yaxis)

    mp.pcolormesh(
        lons, lats, mm2inch(total), clevs, cmap=nwsprecip(), units="inch"
    )
    mp.drawcounties()
    mp.postprocess(pqstr=pqstr, view=False)
    mp.close()


@click.command()
@click.option(
    "--date",
    "dt",
    type=click.DateTime(),
    help="Date to process",
    required=True,
)
@click.option("--realtime", is_flag=True, help="Operate in realtime mode")
def main(dt: datetime, realtime: bool):
    """Go Main Go"""
    doday(dt.date(), realtime)


if __name__ == "__main__":
    main()
