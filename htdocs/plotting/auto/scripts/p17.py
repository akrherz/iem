"""Generate monthly high/low climo plot"""
import datetime
import warnings

import numpy as np
from pandas.io.sql import read_sql
import pandas as pd
import matplotlib.patheffects as PathEffects
from matplotlib.patches import Rectangle
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

warnings.simplefilter("ignore", UserWarning)
PDICT = {"temps": "Plot High/Low Temperatures", "precip": "Plot Precipitation"}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
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
    pgconn_iem = get_dbconn("iem")
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
    df = read_sql(
        "SELECT day, max_tmpf, min_tmpf, pday, "
        "extract(day from day)::int as day_of_month "
        f"from summary_{year} s JOIN "
        "stations t on (t.iemid = s.iemid) WHERE id = %s and network = %s and "
        "day >= %s and day < %s ORDER by day ASC",
        pgconn_iem,
        params=(station, ctx["network"], sts, ets),
        index_col="day_of_month",
    )
    df["accum_pday"] = df["pday"].cumsum()

    # Get the normals
    cdf = read_sql(
        "SELECT high as climo_high, low as climo_low, "
        "extract(day from valid)::int as day_of_month, "
        "precip as climo_precip from ncdc_climate81 where station = %s and "
        "extract(month from valid) = %s ORDER by valid ASC",
        pgconn_coop,
        params=(ctx["_nt"].sts[station]["ncdc81"], month),
        index_col="day_of_month",
    )
    df = cdf.join(df)
    df["accum_climo_precip"] = df["climo_precip"].cumsum()
    df["depart_precip"] = df["accum_pday"] - df["accum_climo_precip"]
    (ctx["fig"], ax) = plt.subplots(1, 1)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height * 0.94])

    for day in weekends:
        rect = Rectangle(
            [day - 0.5, -100], 1, 300, facecolor="#EEEEEE", edgecolor="None"
        )
        ax.add_patch(rect)
    ax.set_xlim(0.5, days + 0.5)
    ax.set_xticks(range(1, days + 1))
    ax.set_xticklabels(np.arange(1, days + 1), fontsize=8)
    ax.set_xlabel(sts.strftime("%B %Y"))

    if ctx["_nt"].sts[station]["ncdc81"] is None:
        subtitle = "Daily climatology unavailable for site"
    else:
        subtitle = ("NCDC 1981-2010 Climate Site: %s") % (
            ctx["_nt"].sts[station]["ncdc81"],
        )

    ax.text(
        0,
        1.1,
        ("[%s] %s :: %s for %s\n%s")
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            "Hi/Lo Temps" if ctx["p"] == "temps" else "Precipitation",
            sts.strftime("%b %Y"),
            subtitle,
        ),
        transform=ax.transAxes,
        ha="left",
        va="bottom",
    )

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
    if df["pday"].notnull().any():
        ax.bar(
            df.index.values + 0.2,
            df["pday"].values,
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

    ax.set_ylim(ymin, ymax)
    ax.legend(
        bbox_to_anchor=(-0.1, 1.01, 1.2, 0.102),
        loc=3,
        ncol=4,
        mode="expand",
        borderaxespad=0.0,
    )


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
    if not all(pd.isnull(df["max_tmpf"])):
        ax.bar(
            df.index.values - 0.3,
            df["max_tmpf"].values,
            fc="r",
            ec="k",
            width=0.3,
            linewidth=0.6,
            label="Ob High",
        )
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
    if not all(pd.isnull(df["max_tmpf"])):
        for _, row in df.iterrows():
            if np.isnan(row["max_tmpf"]) or np.isnan(row["min_tmpf"]):
                i += 1
                continue
            txt = ax.text(
                i + 1 - 0.15,
                row["max_tmpf"] + 0.5,
                "%.0f" % (row["max_tmpf"],),
                fontsize=10,
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
                "%.0f" % (row["min_tmpf"],),
                fontsize=10,
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

    ax.legend(
        bbox_to_anchor=(0.0, 1.01, 1.0, 0.102),
        loc=3,
        ncol=4,
        mode="expand",
        borderaxespad=0.0,
    )


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    common(ctx)
    if ctx["p"] == "precip":
        do_precip_plot(ctx)
    else:
        do_temperature_plot(ctx)

    return ctx["fig"], ctx["df"]


if __name__ == "__main__":
    plotter(
        {"month": 10, "year": 2020, "station": "MULM4", "network": "MI_DCP"}
    )
