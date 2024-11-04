"""
This plot presents the weekly change in a given USDA NASS Crop
Progress report variable.  The units of the change are expressed as percentage
points and not a true percentage.  For example, if the first value was 30% and
the next value was 50%, the change in percentage points is 20.
"""

from datetime import datetime, timedelta

import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
from matplotlib.colorbar import ColorbarBase
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes, get_cmap
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context
from sqlalchemy import text

PDICT = {
    "PCT PLANTED": "Planting",
    "PCT EMERGED": "Emerged",
    "PCT DENTED": "Percent Dented",
    "PCT COLORING": "Percent Coloring",
    "PCT SETTING PODS": "Percent Setting Pods",
    "PCT DROPPING LEAVES": "Percent Dropping Leaves",
    "PCT HARVESTED": "Harvest (Grain)",
}

PDICT2 = {"CORN": "Corn", "SOYBEANS": "Soybean"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 3600, "nass": True, "data": True}
    today = datetime.today()
    desc["arguments"] = [
        dict(type="state", name="state", default="IA", label="Select State:"),
        dict(
            type="year",
            min=1979,
            name="syear",
            default=1979,
            label="Start Year for Plot:",
        ),
        dict(
            type="year",
            min=1979,
            name="eyear",
            default=today.year,
            label="End Year for Plot:",
        ),
        dict(
            type="select",
            name="unit_desc",
            default="PCT PLANTED",
            options=PDICT,
            label="Which Operation?",
        ),
        dict(
            type="select",
            name="commodity_desc",
            default="CORN",
            options=PDICT2,
            label="Which Crop?",
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def get_data(ctx):
    """The data we want and the data we need"""
    unit_desc = ctx["unit_desc"].upper()
    commodity_desc = ctx["commodity_desc"].upper()

    util_practice_desc = (
        "GRAIN"
        if (unit_desc == "PCT HARVESTED" and commodity_desc == "CORN")
        else "ALL UTILIZATION PRACTICES"
    )
    params = {
        "cd": commodity_desc,
        "ud": unit_desc,
        "state": ctx["state"][:2],
        "upd": util_practice_desc,
        "syear": ctx["syear"],
        "eyear": ctx["eyear"],
    }
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text("""
            select year, week_ending, num_value, state_alpha
            from nass_quickstats
            where commodity_desc = :cd and statisticcat_desc = 'PROGRESS'
            and unit_desc = :ud and state_alpha = :state and
            util_practice_desc = :upd and year >= :syear and year <= :eyear
            and num_value is not null
            ORDER by state_alpha, week_ending
        """),
            conn,
            params=params,
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No results found for query!")
    df["week_ending"] = pd.to_datetime(df["week_ending"])
    df["doy"] = pd.to_numeric(df["week_ending"].dt.strftime("%j"))
    df = df.set_index("week_ending")
    df["delta"] = df.groupby("year")["num_value"].diff().fillna(0)
    return df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    df = get_data(ctx)

    cmap = get_cmap(ctx["cmap"])
    maxval = df["delta"].max()
    if maxval > 50:
        bins = np.arange(0, 101, 10)
    elif maxval > 25:
        bins = np.arange(0, 51, 5)
    else:
        bins = np.arange(0, 21, 2)
    bins[0] = 0.01
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    title = (
        f"USDA NASS Weekly {ctx['unit_desc']} "
        f"{PDICT2.get(ctx['commodity_desc'])} Progress for "
        f"{state_names[ctx['state']]}, % {PDICT.get(ctx['unit_desc'])} over "
        "weekly periods"
    )
    subtitle = "yearly max labelled on left hand side"

    (fig, ax) = figure_axes(apctx=ctx, title=title, subtitle=subtitle)

    yearmax = df[["year", "delta"]].groupby("year").max()
    for year, df2 in df.groupby("year"):
        for _, row in df2.iterrows():
            # NOTE: minus 3.5 to center the 7 day bar
            ax.bar(
                row["doy"] - 3.5,
                1,
                bottom=year - 0.5,
                width=7,
                ec="None",
                fc=cmap(norm([row["delta"]]))[0],
            )

    sts = datetime(2000, 1, 1) + timedelta(days=int(df["doy"].min()))
    ets = datetime(2000, 1, 1) + timedelta(days=int(df["doy"].max()))
    now = sts
    interval = timedelta(days=1)
    jdays = []
    labels = []
    while now < ets:
        if now.day in [1, 8, 15, 22]:
            fmt = "%-d\n%b" if now.day == 1 else "%-d"
            jdays.append(int(now.strftime("%j")))
            labels.append(now.strftime(fmt))
        now += interval

    ax.set_xticks(jdays)
    ax.set_xticklabels(labels)

    minyear = df["year"].min()
    maxyear = df["year"].max()
    ax.set_yticks(range(minyear, maxyear + 1))
    ylabels = []
    for yr in range(minyear, maxyear + 1):
        if yr % 5 == 0:
            ylabels.append(f"{yr} {yearmax.at[yr, 'delta']:.0f}")
        else:
            ylabels.append(f"{yearmax.at[yr, 'delta']:.0f}")
    ax.set_yticklabels(ylabels, fontsize=10)

    ax.set_ylim(minyear - 0.5, maxyear + 0.5)
    ax.set_xlim(min(jdays), max(jdays))
    ax.grid(linestyle="-", linewidth="0.5", color="#EEEEEE", alpha=0.7)

    ax.set_position([0.13, 0.1, 0.71, 0.78])
    cax = fig.add_axes(
        [0.86, 0.12, 0.03, 0.75], frameon=False, yticks=[], xticks=[]
    )
    cb = ColorbarBase(cax, norm=norm, cmap=cmap)
    cb.set_label("% Acres")

    return fig, df
