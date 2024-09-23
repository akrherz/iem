"""
Generate an animated GIF of HRRR forecasted 1km reflectivity

Run from hrrr_jobs.py
"""

import glob
import subprocess
import tempfile
from zoneinfo import ZoneInfo

import click
import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
import xarray as xr
from pyiem.plot import MapPlot, ramp2df
from pyiem.plot.colormaps import radar_ptype
from pyiem.reference import Z_FILL
from pyiem.util import archive_fetch, logger

LOG = logger()
HOURS = [18] * 24
for _hr in range(0, 24, 6):
    HOURS[_hr] = 48


def run(tmpdir, valid, routes):
    """Generate the plot for the given UTC time"""
    lats = None
    lons = None
    i = 0
    rampdf = ramp2df("composite_n0q")
    cmap = mpcolors.ListedColormap(rampdf[["r", "g", "b"]].to_numpy() / 256)
    cmap.set_under("white")

    colors = radar_ptype()
    norm = mpcolors.BoundaryNorm(np.arange(0, 56, 2.5), len(colors["rain"]))
    ppath = valid.strftime("%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.refd.grib2")
    with archive_fetch(ppath) as fn:
        if fn is None:
            LOG.warning("missing %s, aborting GIF generation", fn)
            return
        ds = xr.open_dataset(fn)

        for step, toffset in enumerate(ds.step.values):
            now = pd.Timestamp(ds.time.values + toffset).to_pydatetime()
            now = now.astimezone(ZoneInfo("America/Chicago"))
            if lats is None:
                lats = ds.latitude.values
                lons = ds.longitude.values
            mp = MapPlot(
                sector="midwest",
                axisbg="tan",
                title=(
                    f"{valid:%-d %b %Y %H} UTC "
                    "NCEP HRRR 1 km AGL Reflectivity"
                ),
                subtitle=f"valid: {now:%-d %b %Y %I:%M %p %Z}",
            )
            refd = np.ma.masked_where(ds.refd[step] < 5, ds.refd[step])
            for typ in ["rain", "snow", "frzr", "icep"]:
                cmap = mpcolors.ListedColormap(colors[typ])
                ref = np.ma.masked_where(ds[f"c{typ}"][i] < 0.01, refd)
                mp.panels[0].pcolormesh(
                    lons,
                    lats,
                    ref[:-1, :-1],  # hack around pcolormesh grid size demands
                    norm=norm,
                    cmap=cmap,
                    zorder=Z_FILL,
                )
            mp.draw_radar_ptype_legend()
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
