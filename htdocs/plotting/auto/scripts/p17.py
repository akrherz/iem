"""Generate monthly high/low climo plot"""
import datetime
import warnings

import numpy as np
from pandas.io.sql import read_sql
import pandas as pd
import requests
import matplotlib.patheffects as PathEffects
from matplotlib.patches import Rectangle
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn

warnings.simplefilter("ignore", UserWarning)
PDICT = {"temps": "Plot High/Low Temperatures", "precip": "Plot Precipitation"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["cache"] = 300
    today = datetime.date.today()
    mo = today.month
    yr = today.year
    desc["data"] = True
    desc[
        "description"
    ] = """Daily plot of observed high and low temperatures or precipitation
    along with the daily climatology for the nearest (sometimes same) location.
    The vertical highlighted stripes on the plot are just the weekend dates.
    """
    desc["arguments"] = [
        dict(
            type="zstation",
            name="station",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(type="month", name="month", default=mo, label="Select Month"),
        dict(
            type="year",
            name="year",
            default=yr,
            label="Select Year",
            minvalue=2000,
        ),
        dict(
            type="select",
            options=PDICT,
            default="temps",
            label="Select Plot Type:",
            name="p",
        ),
    ]
    return desc


def common(ctx):
    """Do things common to both plots."""
    pgconn_coop = get_dbconn("coop")
    station = ctx["station"]
    year = ctx["year"]
    month = ctx["month"]

    sts = datetime.date(year, month, 1)
    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)
    days = int((ets - sts).days)
    weekends = []
    now = sts
    while now < ets:
        if now.weekday() in [5, 6]:
            weekends.append(now.day)
        now += datetime.timedelta(days=1)
    req = requests.get(
        f"http://mesonet.agron.iastate.edu/api/1/daily.json?station={station}&"
        f"network={ctx['network']}&year={year}&month={month}",
        timeout=15,
    )
    if req.status_code != 200:
        raise ValueError("Unable to fetch data from API service.")
    jsn = req.json()
    df = pd.DataFrame(jsn["data"])
    if not df.empty:
        df["day_of_month"] = pd.to_datetime(df["date"]).dt.day
        df["accum_pday"] = df["precip"].cumsum()
        df = df.set_index("day_of_month")
    # Special case of climate districts and statewide avgs
    table = "ncei_climate91"
    clcol = "ncei91"
    if ctx["network"].endswith("CLIMATE") and (
        station.endswith("0000") or station[2] == "C"
    ):
        table = "climate"
        clcol = "climate_site"
        subtitle = "Climatology provided by period of record averages"
    else:
        if ctx["_nt"].sts[station]["ncei91"] is None:
            subtitle = "Daily climatology unavailable for site"
        else:
            subtitle = (
                "NCEI 1991-2020 Climate Site: "
                f"{ctx['_nt'].sts[station]['ncei91']}"
            )
    # Get the normals
    cdf = read_sql(
        "SELECT high as climo_high, low as climo_low, "
        "extract(day from valid)::int as day_of_month, "
        f"precip as climo_precip from {table} where station = %s and "
        "extract(month from valid) = %s ORDER by valid ASC",
        pgconn_coop,
        params=(ctx["_nt"].sts[station][clcol], month),
        index_col="day_of_month",
    )
    df = cdf.join(df)
    df["accum_climo_precip"] = df["climo_precip"].cumsum()
    if "accum_pday" not in df.columns:
        df["accum_pday"] = 0
    df["depart_precip"] = df["accum_pday"] - df["accum_climo_precip"]
    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']} :: "
        f"{'Hi/Lo Temps' if ctx['p'] == 'temps' else 'Precipitation'} "
        f"for {sts:%b %Y}\n"
        f"{subtitle}"
    )
    (ctx["fig"], ax) = figure_axes(title=title, apctx=ctx)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height * 0.94])

    for day in weekends:
        rect = Rectangle(
            [day - 0.5, -100], 1, 300, facecolor="#EEEEEE", edgecolor="None"
        )
        ax.add_patch(rect)
    ax.set_xlim(0.5, days + 0.5)
    ax.set_xticks(range(1, days + 1))
    ax.set_xticklabels(np.arange(1, days + 1))
    ax.set_xlabel(sts.strftime("%B %Y"), fontsize="larger")
    ax.yaxis.grid(linestyle="-")
    ctx["df"] = df


def do_precip_plot(ctx):
    """Make the precipitation plot."""
    ax = ctx["fig"].gca()
    df = ctx["df"]
    ymax = 1
    ymin = 0
    if df["accum_climo_precip"].max() > 0:
        ax.plot(
            df.index.values,
            df["accum_climo_precip"].values,
            zorder=3,
            color="r",
            label="Accum Avg",
        )
        ymax = df["accum_climo_precip"].max() + 0.5
    if df["depart_precip"].notnull().any():
        ax.bar(
            df.index.values - 0.2,
            df["depart_precip"].values,
            width=0.4,
            align="center",
            zorder=3,
            color="r",
            label="Accum Diff",
        )
        ymin = min([0, df["depart_precip"].min() - 0.5])
    if "precip" in df.columns and df["precip"].notnull().any():
        ax.bar(
            df.index.values + 0.2,
            df["precip"].values,
            width=0.4,
            align="center",
            zorder=3,
            color="b",
            label="Daily Precip",
        )
        ax.plot(
            df.index.values,
            df["accum_pday"].values,
            zorder=4,
            color="b",
            label="Accum Obs",
        )
    ax.set_ylabel("Precipitation [inch]", fontsize="large")
    ax.set_ylim(ymin, ymax)


def do_temperature_plot(ctx):
    """Make the temperature plot."""
    ax = ctx["fig"].gca()
    df = ctx["df"]
    if df["climo_high"].notnull().any():
        ax.plot(
            df.index.values,
            df["climo_high"].values,
            zorder=3,
            marker="o",
            color="pink",
            label="Climate High",
        )
        ax.plot(
            df.index.values,
            df["climo_low"].values,
            zorder=3,
            marker="o",
            color="skyblue",
            label="Climate Low",
        )
    if "max_tmpf" in df.columns and not all(pd.isnull(df["max_tmpf"])):
        ax.bar(
            df.index.values - 0.3,
            df["max_tmpf"].values,
            fc="r",
            ec="k",
            width=0.3,
            linewidth=0.6,
            label="Ob High",
        )
        if "min_tmpf" in df.columns and not all(pd.isnull(df["min_tmpf"])):
            ax.bar(
                df.index.values,
                df["min_tmpf"].values,
                fc="b",
                ec="k",
                width=0.3,
                linewidth=0.6,
                label="Ob Low",
            )
    else:
        ax.text(0.5, 0.5, "No Data Found", transform=ax.transAxes, ha="center")
        ax.set_ylim(0, 1)

    i = 0
    if "max_tmpf" in df.columns and not all(pd.isnull(df["max_tmpf"])):
        for _, row in df.iterrows():
            if pd.isna(row["max_tmpf"]) or pd.isna(row["min_tmpf"]):
                i += 1
                continue
            txt = ax.text(
                i + 1 - 0.15,
                row["max_tmpf"] + 0.5,
                f"{row['max_tmpf']:.0f}",
                ha="center",
                va="bottom",
                color="k",
            )
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=2, foreground="w")]
            )
            txt = ax.text(
                i + 1 + 0.15,
                row["min_tmpf"] + 0.5,
                f"{row['min_tmpf']:.0f}",
                ha="center",
                va="bottom",
                color="k",
            )
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=2, foreground="w")]
            )
            i += 1
        ax.set_ylim(
            np.nanmin([df["climo_low"].min(), df["min_tmpf"].min()]) - 5,
            np.nanmax([df["climo_high"].max(), df["max_tmpf"].max()]) + 5,
        )
    ax.set_ylabel(r"Temperature $^\circ$F")


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    common(ctx)
    if ctx["p"] == "precip":
        do_precip_plot(ctx)
    else:
        do_temperature_plot(ctx)
    ctx["fig"].gca().legend(
        bbox_to_anchor=(0.0, 1.01, 1.0, 0.102),
        loc=3,
        ncol=4,
        mode="expand",
        borderaxespad=0.0,
    )
    return ctx["fig"], ctx["df"]


if __name__ == "__main__":
    plotter(
        {"month": 5, "year": 2012, "station": "MIRT2", "network": "TX_DCP"}
    )
