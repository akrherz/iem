"""Overcast 2-D Histogram"""
import datetime

import matplotlib.colors as mpcolors
import numpy as np
import numpy.ma as ma
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes, get_cmap
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot presents a 2-D histogram of overcast
    conditions reported by the automated sensor.  Please note that the yaxis
    uses an irregular spacing.
    """
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """
            select extract(doy from valid) as doy,
            greatest(skyl1, skyl2, skyl3, skyl4) as sky from alldata
            WHERE station = %s and
            (skyc1 = 'OVC' or skyc2 = 'OVC' or skyc3 = 'OVC' or skyc4 = 'OVC')
            and valid > '1973-01-01' and report_type = 3
        """,
            conn,
            params=(station,),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("Error, no results returned!")

    w = np.arange(1, 366, 7)
    z = np.append(
        np.arange(100, 5001, 100),
        np.append(
            np.arange(5500, 10001, 500),
            np.arange(11000, 31001, 1000),
        ),
    )

    H, xedges, yedges = np.histogram2d(
        df["sky"].values, df["doy"].values, bins=(z, w)
    )
    rows = []
    for i, x in enumerate(xedges[:-1]):
        for j, y in enumerate(yedges[:-1]):
            rows.append(dict(ceiling=x, doy=y, count=H[i, j]))
    resdf = pd.DataFrame(rows)

    H = ma.array(H)
    H.mask = np.where(H < 1, True, False)

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    syear = max([1973, ab.year])

    title = (
        f"({syear}-{datetime.date.today().year}) {ctx['_sname']}:: "
        "Ceilings Frequency\n"
        "Level at which Overcast Conditions Reported"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    bounds = np.arange(0, 1.2, 0.1)
    bounds = np.concatenate((bounds, np.arange(1.2, 2.2, 0.2)))
    cmap = get_cmap(ctx["cmap"])
    cmap.set_under("#F9CCCC")
    norm = mpcolors.BoundaryNorm(bounds, cmap.N)

    years = (datetime.date.today().year - syear) + 1.0
    c = ax.imshow(
        H / years, aspect="auto", interpolation="nearest", norm=norm, cmap=cmap
    )
    ax.set_ylim(-0.5, len(z) - 0.5)
    idx = [0, 4, 9, 19, 29, 39, 49, 54, 59, 64, 69, 74, 79]
    ax.set_yticks(idx)
    ax.set_yticklabels(z[idx])
    ax.set_ylabel("Overcast Level [ft AGL], irregular scale")
    ax.set_xlabel("Week of the Year")
    ax.set_xticks(np.arange(1, 55, 7))
    ax.set_xticklabels(
        (
            "Jan 1",
            "Feb 19",
            "Apr 8",
            "May 27",
            "Jul 15",
            "Sep 2",
            "Oct 21",
            "Dec 9",
        )
    )
    b = fig.colorbar(c)
    b.set_label("Hourly Obs per week per year")
    return fig, resdf


if __name__ == "__main__":
    plotter({})
