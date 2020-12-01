"""NASS yearly bar plot."""
from collections import OrderedDict
import datetime

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot import get_cmap
from pyiem.plot.use_agg import plt
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound
from matplotlib.colorbar import ColorbarBase
import matplotlib.colors as mpcolors
import numpy as np

PDICT = OrderedDict(
    [
        ("PCT PLANTED", "Planting"),
        ("PCT EMERGED", "Emerged"),
        ("PCT DENTED", "Percent Dented"),
        ("PCT COLORING", "Percent Coloring"),
        ("PCT SETTING PODS", "Percent Setting Pods"),
        ("PCT DROPPING LEAVES", "Percent Dropping Leaves"),
        ("PCT HARVESTED", "Harvest (Grain)"),
    ]
)
PDICT2 = OrderedDict([("CORN", "Corn"), ("SOYBEANS", "Soybean")])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["cache"] = 3600
    desc["data"] = True
    desc["nass"] = True
    desc[
        "description"
    ] = """This plot presents the weekly change in a given USDA NASS Crop
    Progress report variable.
    """
    today = datetime.datetime.today()
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
    pgconn = get_dbconn("coop")
    unit_desc = ctx["unit_desc"].upper()
    commodity_desc = ctx["commodity_desc"].upper()

    util_practice_desc = (
        "GRAIN"
        if (unit_desc == "PCT HARVESTED" and commodity_desc == "CORN")
        else "ALL UTILIZATION PRACTICES"
    )
    params = (
        commodity_desc,
        unit_desc,
        ctx["state"][:2],
        util_practice_desc,
        ctx["syear"],
        ctx["eyear"],
    )
    df = read_sql(
        """
        select year, week_ending, num_value, state_alpha from nass_quickstats
        where commodity_desc = %s and statisticcat_desc = 'PROGRESS'
        and unit_desc = %s and state_alpha = %s and
        util_practice_desc = %s and year >= %s and year <= %s
        and num_value is not null
        ORDER by state_alpha, week_ending
    """,
        pgconn,
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
    """ Go """
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

    (fig, ax) = plt.subplots(1, 1, figsize=(6.4, 6.4))

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

    sts = datetime.datetime(2000, 1, 1) + datetime.timedelta(
        days=int(df["doy"].min())
    )
    ets = datetime.datetime(2000, 1, 1) + datetime.timedelta(
        days=int(df["doy"].max())
    )
    now = sts
    interval = datetime.timedelta(days=1)
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
            ylabels.append("%s %.0f" % (yr, yearmax.at[yr, "delta"]))
        else:
            ylabels.append("%.0f" % (yearmax.at[yr, "delta"],))
    ax.set_yticklabels(ylabels, fontsize=10)

    ax.set_ylim(minyear - 0.5, maxyear + 0.5)
    ax.set_xlim(min(jdays), max(jdays))
    ax.grid(linestyle="-", linewidth="0.5", color="#EEEEEE", alpha=0.7)
    ax.set_title(
        (
            "USDA NASS Weekly %s %s Progress\n"
            "%s %% %s over weekly periods\n"
            "yearly max labelled on left hand side"
        )
        % (
            ctx["unit_desc"],
            PDICT2.get(ctx["commodity_desc"]),
            state_names[ctx["state"]],
            PDICT.get(ctx["unit_desc"]),
        )
    )

    ax.set_position([0.13, 0.1, 0.71, 0.78])
    cax = plt.axes(
        [0.86, 0.12, 0.03, 0.75], frameon=False, yticks=[], xticks=[]
    )
    cb = ColorbarBase(cax, norm=norm, cmap=cmap)
    cb.set_label("% Acres")

    return fig, df


if __name__ == "__main__":
    plotter(dict(commodity_desc="CORN", unit_desc="PCT HARVESTED"))
