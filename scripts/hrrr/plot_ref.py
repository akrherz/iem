"""
Generate an animated GIF of HRRR forecasted 1km reflectivity

Run from RUN_40AFTER.sh and for the previous hour's HRRR run
"""

import datetime
import glob
import subprocess
import tempfile
from zoneinfo import ZoneInfo

import click
import matplotlib.colors as mpcolors
import numpy as np
import pygrib
import pyiem.reference as ref
from pyiem.plot import MapPlot, ramp2df
from pyiem.util import archive_fetch, logger

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


def run(tmpdir, valid, routes):
    """Generate the plot for the given UTC time"""
    lats = None
    lons = None
    i = 0
    rampdf = ramp2df("composite_n0q")
    cmap = mpcolors.ListedColormap(rampdf[["r", "g", "b"]].to_numpy() / 256)
    cmap.set_under("white")

    fn = valid.strftime("%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.refd.grib2")
    with archive_fetch(fn) as res:
        if res is None:
            LOG.warning("missing %s, aborting GIF generation", fn)
            return
        grbs = pygrib.open(res)

        for minute in range(0, HOURS[valid.hour] * 60 + 1, 15):
            is_minute = minute <= (18 * 60)  # grib sucks
            if not is_minute and minute % 60 != 0:
                continue
            now = valid + datetime.timedelta(minutes=minute)
            now = now.astimezone(ZoneInfo("America/Chicago"))
            grbs.seek(0)

            try:
                gs = grbs.select(
                    indicatorOfUnitOfTimeRange=0 if is_minute else 1,
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
                title=(
                    f"{valid:%-d %b %Y %H} UTC "
                    "NCEP HRRR 1 km AGL Reflectivity"
                ),
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
            pngfn = f"{tmpdir}/hrrr_ref_{i:03.0f}.png"
            mp.postprocess(filename=pngfn)
            mp.close()
            subprocess.call(["magick", pngfn, f"{pngfn[:-4]}.gif"])

            i += 1

    # Generate anim GIF
    gifs = glob.glob(f"{tmpdir}/hrrr_ref_???.gif")
    gifs.sort()
    subprocess.call(
        [
            "gifsicle",
            "--loopcount=0",
            "--delay=50",
            "-o",
            f"{tmpdir}/hrrr_ref.gif",
            *gifs,
        ],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    pqstr = (
        f"plot {routes} {valid:%Y%m%d%H%M} model/hrrr/hrrr_1km_ref.gif "
        f"model/hrrr/hrrr_1km_ref_{valid.hour:02.0f}.gif gif"
    )
    subprocess.call(
        ["pqinsert", "-p", pqstr, f"{tmpdir}/hrrr_ref.gif"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )


@click.command()
@click.option("--valid", required=True, type=click.DateTime())
@click.option("--is-realtime", default=False, is_flag=True)
def main(valid, is_realtime):
    """Go Main"""
    valid = valid.replace(tzinfo=ZoneInfo("UTC"))
    routes = "ac" if is_realtime else "a"
    LOG.info("valid: %s routes: %s", valid, routes)

    # See if we already have output
    fn = valid.strftime("%Y/%m/%d/model/hrrr/hrrr_1km_ref_%H.gif")
    with archive_fetch(fn) as res:
        if res is None:
            LOG.info("archive GIF missing %s, running", fn)
            with tempfile.TemporaryDirectory() as tmpdir:
                run(tmpdir, valid, routes)


if __name__ == "__main__":
    main()
