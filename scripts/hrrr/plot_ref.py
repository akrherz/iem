"""
Generate an animated GIF of HRRR forecasted 1km reflectivity

Run from RUN_40AFTER.sh and for the previous hour's HRRR run
"""
import datetime
import subprocess
import sys
import os

import numpy as np
import pytz
import pygrib
import matplotlib.colors as mpcolors
from pyiem.plot import MapPlot, ramp2df
import pyiem.reference as ref
from pyiem.util import utc, logger

LOG = logger()
HOURS = [18] * 24
for _hr in range(0, 24, 6):
    HOURS[_hr] = 48


def compute_bounds(lons, lats):
    """figure out a minimum box to extract data from, save CPU"""
    dist = ((lats - ref.MW_NORTH) ** 2 + (lons - ref.MW_WEST) ** 2) ** 0.5
    # pylint: disable=unbalanced-tuple-unpacking
    x2, y1 = np.unravel_index(dist.argmin(), dist.shape)
    dist = ((lats - ref.MW_SOUTH) ** 2 + (lons - ref.MW_EAST) ** 2) ** 0.5
    # pylint: disable=unbalanced-tuple-unpacking
    x1, y2 = np.unravel_index(dist.argmin(), dist.shape)
    return x1 - 100, x2 + 100, y1 - 100, y2 + 100


def run(valid, routes):
    """Generate the plot for the given UTC time"""
    fn = valid.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.refd.grib2"
    )

    if not os.path.isfile(fn):
        LOG.warning("hrrr/plot_ref missing %s", fn)
        return
    grbs = pygrib.open(fn)

    lats = None
    lons = None
    i = 0
    rampdf = ramp2df("composite_n0q")
    cmap = mpcolors.ListedColormap(rampdf[["r", "g", "b"]].to_numpy() / 256)
    cmap.set_under("white")
    for minute in range(0, HOURS[valid.hour] * 60 + 1, 15):
        is_minute = minute <= (18 * 60)  # grib sucks
        if not is_minute and minute % 60 != 0:
            continue
        now = valid + datetime.timedelta(minutes=minute)
        now = now.astimezone(pytz.timezone("America/Chicago"))
        grbs.seek(0)

        try:
            gs = grbs.select(
                indicatorOfUnitOfTimeRange=0 if is_minute else 1,  # Grib 4.4
                forecastTime=minute if is_minute else int(minute / 60),
            )
        except ValueError:
            LOG.info("select failure: %s %s", valid, minute)
            continue
        if lats is None:
            lats, lons = gs[0].latlons()
            x1, x2, y1, y2 = compute_bounds(lons, lats)
            lats = lats[x1:x2, y1:y2]
            lons = lons[x1:x2, y1:y2]

        reflect = gs[0]["values"][x1:x2, y1:y2]
        reflect = np.where(reflect < -9, -100, reflect)
        mp = MapPlot(
            sector="midwest",
            axisbg="tan",
            title=f"{valid:%-d %b %Y %H} UTC NCEP HRRR 1 km AGL Reflectivity",
            subtitle=f"valid: {now:%-d %b %Y %I:%M %p %Z}",
        )
        levels = [-32, -30]
        levels.extend(range(-10, 96, 5))
        mp.pcolormesh(
            lons,
            lats,
            reflect,
            range(-30, 96, 4),
            spacing="proportional",
            cmap=cmap,
            units="dBZ",
            clip_on=False,
            clevstride=5,
        )
        pngfn = f"/tmp/hrrr_ref_{valid:%Y%m%d%H}_{i:03.0f}.png"
        mp.postprocess(filename=pngfn)
        mp.close()
        subprocess.call(["convert", pngfn, f"{pngfn[:-4]}.gif"])

        i += 1

    # Generate anim GIF
    subprocess.call(
        (
            "gifsicle --loopcount=0 --delay=50 "
            f"/tmp/hrrr_ref_{valid:%Y%m%d%H}_???.gif > "
            f"/tmp/hrrr_ref_{valid:%Y%m%d%H}.gif"
        ),
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    pqstr = (
        f"plot {routes} {valid:%Y%m%d%H%M} model/hrrr/hrrr_1km_ref.gif "
        f"model/hrrr/hrrr_1km_ref_{valid.hour:02.0f}.gif gif"
    )
    subprocess.call(
        f"pqinsert -p '{pqstr}' /tmp/hrrr_ref_{valid:%Y%m%d%H}.gif",
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    subprocess.call(f"rm -f /tmp/hrrr_ref_{valid:%Y%m%d%H}*", shell=True)


def main(argv):
    """Go Main"""
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
    routes = "ac" if argv[5] == "RT" else "a"
    LOG.info("valid: %s routes: %s", valid, routes)

    # See if we already have output
    fn = valid.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/hrrr_1km_ref_%H.gif"
    )
    if not os.path.isfile(fn):
        run(valid, routes)


if __name__ == "__main__":
    main(sys.argv)
