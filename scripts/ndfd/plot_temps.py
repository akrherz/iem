"""Generate some plots.

Called from RUN_10_AFTER.sh
"""

from datetime import datetime, timedelta

import click
import numpy as np
from metpy.units import masked_array, units
from pyiem.iemre import daily_offset
from pyiem.meteorology import gdd
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot
from pyiem.util import ncopen, utc


def plot_gdd(ts):
    """Generate our plot."""
    nc = ncopen(ts.strftime("/mesonet/data/ndfd/%Y%m%d%H_ndfd.nc"))
    # compute our daily GDDs
    gddtot = np.zeros(np.shape(nc.variables["lon"][:]))
    for i in range(7):
        gddtot += gdd(
            units("degK") * nc.variables["high_tmpk"][i, :, :],
            units("degK") * nc.variables["low_tmpk"][i, :, :],
        )
    cnc = ncopen("/mesonet/data/ndfd/ndfd_dailyc.nc")
    offset = daily_offset(ts)
    avggdd = np.sum(cnc.variables["gdd50"][offset : offset + 7], 0)
    data = gddtot - np.where(avggdd < 1, 1, avggdd)

    subtitle = (
        "Based on National Digital Forecast Database (NDFD) "
        f"00 UTC Forecast made {ts:%-d %b %Y}"
    )
    t2 = ts + timedelta(days=6)
    mp = MapPlot(
        title=(
            f"NWS NDFD 7 Day ({ts:%-d %b} through {t2:%-d %b}) "
            "GDD50 Departure from Avg"
        ),
        subtitle=subtitle,
        sector="midwest",
    )
    mp.pcolormesh(
        nc.variables["lon"][:],
        nc.variables["lat"][:],
        data,
        np.arange(-80, 81, 20),
        cmap=get_cmap("RdBu_r"),
        units=r"$^\circ$F",
        spacing="proportional",
    )
    mp.drawcounties()
    pqstr = (
        f"data c {ts:%Y%m%d%H%M} summary/cb_ndfd_7day_gdd.png "
        "summary/cb_ndfd_7day_gdd.png png"
    )
    mp.postprocess(pqstr=pqstr)
    mp.close()
    nc.close()


def plot_maxmin(ts, field):
    """Generate our plot."""
    nc = ncopen(ts.strftime("/mesonet/data/ndfd/%Y%m%d%H_ndfd.nc"))
    func = np.max if field == "high_tmpk" else np.min
    data = func(nc.variables[field][:], 0)
    data = masked_array(data, units.degK).to(units.degF).m

    subtitle = (
        "Based on National Digital Forecast Database (NDFD) "
        f"00 UTC Forecast made {ts:%-d %b %Y}"
    )
    t2 = ts + timedelta(days=6)
    tt = "Maximum" if field == "high_tmpk" else "Minimum"
    mp = MapPlot(
        title=(
            f"NWS NDFD 7 Day ({ts:%-d %b} through {t2:%-d %b}) "
            f"{tt} Temperature"
        ),
        subtitle=subtitle,
        sector="midwest",
    )
    mp.pcolormesh(
        nc.variables["lon"][:],
        nc.variables["lat"][:],
        data,
        np.arange(10, 121, 10),
        cmap=get_cmap("jet"),
        units="Degrees F",
    )
    mp.drawcounties()
    tt = "max" if field == "high_tmpk" else "min"
    pqstr = (
        f"data c {ts:%Y%m%d%H%M} summary/cb_ndfd_7day_{tt}.png "
        f"summary/cb_ndfd_7day_{tt}.png png"
    )
    mp.postprocess(pqstr=pqstr)
    mp.close()
    nc.close()


@click.command()
@click.option("--date", "dt", type=click.DateTime(), required=True)
def main(dt: datetime):
    """Run for the given args."""
    ts = utc(dt.year, dt.month, dt.day)
    plot_gdd(ts)
    plot_maxmin(ts, "high_tmpk")
    plot_maxmin(ts, "low_tmpk")


if __name__ == "__main__":
    main()
