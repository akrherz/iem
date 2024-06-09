"""
This plot presents the combination of monthly
temperature or precipitation departures and El Nino index values.
"""

import datetime

import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

PDICT = {
    "avg_high": "Average High Temperature [F]",
    "avg_temp": "Average Temperature [F]",
    "avg_low": "Average Low Temperature [F]",
    "precip": "Total Precipitation [inch]",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    year = datetime.date.today().year - 7
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="year",
            name="syear",
            default=year,
            label="Start Year of Plot",
            min=1950,
        ),
        dict(
            type="int",
            name="years",
            default="8",
            label="Number of Years to Plot",
        ),
        dict(
            type="select",
            name="var",
            default="avg_temp",
            label="Which Monthly Variable to plot?",
            options=PDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["station"]
    syear = ctx["syear"]
    years = ctx["years"]
    varname = ctx["var"]

    sts = datetime.datetime(syear, 1, 1)
    ets = datetime.datetime(syear + years, 1, 1)
    archiveend = datetime.date.today() + datetime.timedelta(days=1)
    if archiveend.day < 20:
        archiveend = archiveend.replace(day=1)

    with get_sqlalchemy_conn("coop") as conn:
        ndf = pd.read_sql(
            "SELECT anom_34, monthdate from elnino where monthdate >= %s and "
            "monthdate < %s ORDER by monthdate ASC",
            conn,
            params=(sts, ets),
            index_col="monthdate",
        )
        df = pd.read_sql(
            """
        WITH climo2 as (
            SELECT year, month, avg((high+low)/2.), sum(precip),
            avg(high) as avg_high, avg(low) as avg_low
            from alldata where station = %s
            and day < %s GROUP by year, month),
        climo as (
            select month, avg(avg) as t, avg(sum) as p,
            avg(avg_high) as high, avg(avg_low) as low from climo2
            GROUP by month),
        obs as (
            SELECT year, month, avg((high+low)/2.), avg(high) as avg_high,
            avg(low) as avg_low,
            sum(precip) from alldata where station = %s
            and day < %s and year >= %s and year < %s GROUP by year, month)

        SELECT obs.year, obs.month, obs.avg - climo.t as avg_temp,
        obs.avg_high - climo.high as avg_high,
        obs.avg_low - climo.low as avg_low,
        obs.sum - climo.p as precip from
        obs JOIN climo on (climo.month = obs.month)
        ORDER by obs.year ASC, obs.month ASC
        """,
            conn,
            params=(
                station,
                archiveend,
                station,
                archiveend,
                sts.year,
                ets.year,
            ),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["date"] = pd.to_datetime(
        {"year": df["year"], "month": df["month"], "day": 1}
    )
    df = df.set_index("date")
    df["nino34"] = ndf["anom_34"]

    title = (
        f"{ctx['_sname']}:: Monthly Departure of {PDICT.get(varname)} "
        "+ Niño 3.4 Index\n"
        "Climatology computed from present day period of record"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    xticks = []
    xticklabels = []
    for v in df.index:
        if v.month not in [1, 7]:
            continue
        if years > 8 and v.month == 7:
            continue
        if v.month == 1:
            fmt = "%b\n%Y"
        else:
            fmt = "%b"
        xticklabels.append(v.strftime(fmt))
        xticks.append(v)
    while len(xticks) > 9:
        xticks = xticks[::2]
        xticklabels = xticklabels[::2]

    _a = "pink"
    _b = "skyblue"
    if varname == "precip":
        _a, _b = _b, _a
    bars = ax.bar(
        df.index.date,
        df[varname].values,
        fc=_a,
        ec=_a,
        width=30,
        align="center",
    )
    for mybar in bars:
        if mybar.get_height() < 0:
            mybar.set_facecolor(_b)
            mybar.set_edgecolor(_b)

    ax2 = ax.twinx()

    ax2.plot(
        ndf.index.values, ndf["anom_34"].values, zorder=2, color="k", lw=2.0
    )
    ax2.set_ylabel("<-- La Niña :: Niño 3.4 Index (line) :: El Niño -->")
    ax2.set_ylim(-3, 3)

    ax.set_ylabel(f"{PDICT.get(varname)} Departure (bars)")
    ax.grid(True)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(sts, ets)
    maxv = df[varname].abs().max() + 2
    ax.set_ylim(0 - maxv, maxv)

    ax.legend(
        [
            Rectangle((0, 0), 1, 1, fc=_a),
            Rectangle((0, 0), 1, 1, fc=_b),
            Line2D((0, 1), (0, 1), color="k", lw=2),
        ],
        [f"Above Normal {varname}", f"Below Normal {varname}", "Nino 3.5"],
        ncol=3,
        loc="best",
    )

    return fig, df
