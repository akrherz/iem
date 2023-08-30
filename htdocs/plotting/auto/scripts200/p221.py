"""
The NCEP deterministic HRRR model forecast produces a post
processed field that is meant to resemble RADAR reflectivity.  The
lowest 1km HRRR product is plotted along with the IEM mosaic NWS
NEXRAD base reflectivity.

<p><strong>Caution:</strong> This autoplot is very slow to generate,
please be patient!
"""
import datetime
import os
from io import BytesIO

import matplotlib.colors as mpcolors
import numpy as np
import pygrib
from PIL import Image
from pyiem.plot import MapPlot, ramp2df
from pyiem.util import get_autoplot_context, utc

PDICT = {
    "sector": "Plot by State / Sector",
    "cwa": "Plot by NWS CWA / WFO",
}
FONTSIZE = 32


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"data": False, "description": __doc__}
    sts = utc() - datetime.timedelta(hours=5)
    desc["arguments"] = [
        dict(
            type="select",
            name="w",
            default="sector",
            options=PDICT,
            label="Plot for which domain type",
        ),
        dict(
            type="csector",
            name="sector",
            default="IA",
            label="Select state/sector",
        ),
        dict(
            type="networkselect",
            name="cwa",
            default="DMX",
            label="Select WFO / CWA:",
            network="WFO",
        ),
        dict(
            type="datetime",
            name="valid",
            default=sts.strftime("%Y/%m/%d %H00"),
            label="Plot Valid At (UTC Timestamp):",
            min="2014/01/01 0000",
        ),
    ]
    return desc


def mp_factory(ctx):
    """Make"""
    if ctx["w"] == "sector":
        sector = "state" if len(ctx["sector"]) == 2 else ctx["sector"]
        state = ctx["sector"]
        cwa = ""
    else:
        sector = "cwa"
        state = ""
        cwa = ctx["cwa"]
    return MapPlot(
        apctx=ctx,
        sector=sector,
        nologo=True,
        state=state,
        cwa=cwa,
        nocaption=True,
    )


def add_forecast(img, ctx, valid, fhour, x, y):
    """Overlay things."""
    ts = valid - datetime.timedelta(hours=fhour)
    gribfn = ts.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.refd.grib2"
    )
    if not os.path.isfile(gribfn):
        return
    grbs = pygrib.open(gribfn)
    try:
        gs = grbs.select(level=1000, forecastTime=(fhour * 60))
    except ValueError:
        grbs.close()
        return
    ref = gs[0]["values"]
    # HRRR anything below -9 is missing
    ref = np.where(ref < -9, -100, ref)
    if "lats" not in ctx:
        ctx["lats"], ctx["lons"] = gs[0].latlons()
    mp = mp_factory(ctx)
    mp.fig.text(
        0.1,
        0.92,
        f"HRRR Init:{ts:%d/%H} Forecast Hour:{fhour}",
        fontsize=FONTSIZE,
    )
    mp.pcolormesh(
        ctx["lons"],
        ctx["lats"],
        ref,
        range(-30, 96, 4),
        cmap=ctx["cmap"],
        clip_on=False,
        clevstride=5,
    )
    if ctx["w"] != "sector" and ctx["sector"] != "conus":
        mp.drawcounties()
    buf = BytesIO()
    mp.fig.savefig(buf, format="png")
    buf.seek(0)
    tmp = Image.open(buf).resize((512, 386))
    buf.close()
    img.paste(tmp, (x, y))
    del tmp
    mp.close()


def add_obs(img, ctx, valid):
    """Plot the validation."""
    mp = mp_factory(ctx)
    mp.fig.text(
        0.05,
        0.92,
        f"NEXRAD MOSAIC {valid:%Y-%m-%d %H:%M} UTC",
        fontsize=FONTSIZE,
        bbox=dict(color="white"),
    )
    mp.overlay_nexrad(valid)
    if ctx["w"] != "sector" and ctx["sector"] != "conus":
        mp.drawcounties()
    buf = BytesIO()
    mp.fig.savefig(buf, format="png")
    buf.seek(0)
    tmp = Image.open(buf).resize((512, 386))
    buf.close()
    img.paste(tmp, (0, 0))
    del tmp
    mp.close()


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    valid = ctx["valid"].replace(tzinfo=datetime.timezone.utc)
    ramp = ramp2df("composite_n0q")
    ctx["cmap"] = mpcolors.ListedColormap(
        ramp[["r", "g", "b"]].to_numpy() / 256,
    )
    ctx["cmap"].set_under((0, 0, 0, 0))

    width = 512
    height = 386
    img = Image.new("RGB", (width * 4, height * 4))

    add_obs(img, ctx, valid)
    for fhour in range(1, 16):
        row = fhour // 4
        col = fhour % 4
        add_forecast(img, ctx, valid, fhour, width * col, height * row)
    return img


if __name__ == "__main__":
    plotter({})
