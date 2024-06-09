"""yieldfx plot"""

import calendar
import datetime
import os

import pandas as pd
from metpy.units import units
from pyiem.exceptions import NoDataFound
from pyiem.meteorology import gdd
from pyiem.plot import figure_axes
from pyiem.util import c2f, get_autoplot_context, mm2inch

STATIONS = {
    "ames": "Central (Ames)",
    "cobs": "Central (COBS)",
    "crawfordsville": "Southeast (Crawfordsville)",
    "kanawha": "Northern (Kanawha)",
    "lewis": "Southwest (Lewis)",
    "mcnay": "Southern (Chariton/McNay)",
    "muscatine": "Southeast (Muscatine)",
    "nashua": "Northeast (Nashua)",
    "sutherland": "Northwest (Sutherland)",
}

PLOTS = {
    "gdd": "Growing Degree Days [F]",
    "rain": "Precipitation [in]",
    "maxt": "Daily Maximum Temperature [F]",
    "mint": "Daily Minimum Temperature [F]",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="select",
            name="location",
            default="ames",
            label="Select Location:",
            options=STATIONS,
        ),
        dict(
            type="select",
            name="ptype",
            default="gdd",
            label="Select Plot Type:",
            options=PLOTS,
        ),
        dict(type="text", name="sdate", default="mar15", label="Start Date:"),
    ]
    return desc


def load(dirname, location, sdate):
    """Read a file please"""
    data = []
    idx = []
    mindoy = int(sdate.strftime("%j"))
    fn = f"{dirname}/{location}.met"
    if not os.path.isfile(fn):
        raise NoDataFound("Data file was not found.")
    with open(fn, encoding="utf8") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("19") and not line.startswith("20"):
                continue
            tokens = line.split()
            if int(tokens[1]) < mindoy:
                continue
            data.append(tokens)
            ts = datetime.date(int(tokens[0]), 1, 1) + datetime.timedelta(
                days=int(tokens[1]) - 1
            )
            idx.append(ts)
    if len(data[0]) < 10:
        cols = ["year", "doy", "radn", "maxt", "mint", "rain"]
    else:
        cols = [
            "year",
            "doy",
            "radn",
            "maxt",
            "mint",
            "rain",
            "gdd",
            "st4",
            "st12",
            "st24",
            "st50",
            "sm12",
            "sm24",
            "sm50",
        ]
    df = pd.DataFrame(data, index=idx, columns=cols)
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if len(data[0]) < 10:
        df["gdd"] = gdd(
            units("degC") * df["maxt"].values,
            units("degC") * df["mint"].values,
        )
    df["gddcum"] = df.groupby(["year"])["gdd"].apply(lambda x: x.cumsum())
    df["raincum"] = mm2inch(
        df.groupby(["year"])["rain"].apply(lambda x: x.cumsum())
    )
    return df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    location = ctx["location"]
    ptype = ctx["ptype"]
    sdate = datetime.datetime.strptime(ctx["sdate"], "%b%d")
    df = load("/mesonet/share/pickup/yieldfx", location, sdate)
    cdf = load("/opt/iem/scripts/yieldfx/baseline", location, sdate)

    today = datetime.date.today()
    thisyear = (
        df[df["year"] == today.year].copy().reset_index().set_index("doy")
    )

    # Drop extra day from cdf during non-leap year
    if today.year % 4 != 0:
        cdf = cdf[cdf["doy"] < 366]
        df = df[df["doy"] < 366]

    # Create a specialized result dataframe for CSV, Excel output options
    resdf = pd.DataFrame(index=thisyear.index)
    resdf.index.name = "date"
    resdf["doy"] = thisyear.index.values
    resdf = resdf.reset_index().set_index("doy")

    # write current year data back to resdf
    for _v, _u in zip(["gddcum", "raincum"], ["F", "in"]):
        resdf[f"{_v}[{_u}]"] = thisyear[_v]
    for _v in ["mint", "maxt"]:
        resdf[f"{_v}[F]"] = c2f(thisyear[_v].values)
    resdf["rain[in]"] = mm2inch(thisyear["rain"])
    for _ptype, unit in zip(["gdd", "rain"], ["F", "in"]):
        resdf[f"{_ptype}cum_climo[{unit}]"] = cdf.groupby("doy")[
            _ptype + "cum"
        ].mean()
        resdf[f"{_ptype}cum_min[{unit}]"] = df.groupby("doy")[
            _ptype + "cum"
        ].min()
        resdf[f"{_ptype}cum_max[{unit}]"] = df.groupby("doy")[
            _ptype + "cum"
        ].max()
    for _ptype in ["maxt", "mint"]:
        resdf[_ptype + "_climo[F]"] = c2f(
            cdf.groupby("doy")[_ptype].mean().values
        )
        resdf[_ptype + "_min[F]"] = c2f(df.groupby("doy")[_ptype].min().values)
        resdf[_ptype + "_max[F]"] = c2f(df.groupby("doy")[_ptype].max().values)

    (fig, ax) = figure_axes(apctx=ctx)
    if ptype in ["gdd", "rain"]:
        ax.plot(
            thisyear.index.values,
            thisyear[ptype + "cum"],
            zorder=4,
            color="b",
            lw=2,
            label=f"{today.year} Obs + CFS Forecast",
        )
        climo = cdf.groupby("doy")[ptype + "cum"].mean()
        ax.plot(
            climo.index.values,
            climo.values,
            lw=2,
            color="k",
            label="Climatology",
            zorder=3,
        )
        xrng = df.groupby("doy")[ptype + "cum"].max()
        nrng = df.groupby("doy")[ptype + "cum"].min()
        ax.fill_between(
            xrng.index.values,
            nrng.values,
            xrng.values,
            color="tan",
            label="Range",
            zorder=2,
        )
    else:
        ax.plot(
            thisyear.index.values,
            c2f(thisyear[ptype]),
            zorder=4,
            color="b",
            lw=2,
            label=f"{today.year} Obs + CFS Forecast",
        )
        climo = cdf.groupby("doy")[ptype].mean()
        ax.plot(
            climo.index.values,
            c2f(climo.values),
            lw=2,
            color="k",
            label="Climatology",
            zorder=3,
        )
        xrng = df.groupby("doy")[ptype].max()
        nrng = df.groupby("doy")[ptype].min()
        ax.fill_between(
            xrng.index.values,
            c2f(nrng.values),
            c2f(xrng.values),
            color="tan",
            label="Range",
            zorder=2,
        )

    ax.set_title(f"{STATIONS[location]} {PLOTS[ptype]}")
    ax.set_ylabel(PLOTS[ptype])
    ax.legend(loc=(0.03, -0.16), ncol=3, fontsize=12)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_xlim(
        int(sdate.strftime("%j")),
        int(datetime.date(today.year, 12, 1).strftime("%j")),
    )
    pos = ax.get_position()
    ax.set_position([pos.x0, pos.y0 + 0.05, pos.width, pos.height * 0.95])

    return fig, resdf
