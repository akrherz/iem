"""Daily Climatology"""

# third party
import pandas as pd
from pandas.io.sql import read_sql
import matplotlib.dates as mdates
from pyiem.exceptions import NoDataFound
from pyiem.reference import TWITTER_RESOLUTION_INCH
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.plot import fitbox

PDICT = {
    "por": "Period of Record (por) Climatology",
    "1951": "1951-present Climatology",
    "ncei81": "NCEI 1981-2010 Climatology",
    "custom": "Custom Climatology (pick years)",
}
PDICT2 = {
    "0": "No Smoothing Applied",
    "7": "Seven Day Centered Smooth",
    "14": "Fourteen Day Centered Smooth",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This application plots daily climatology for
    a location or two of your choice.  You can pick which climatology to use
    and effectively build a difference plot when picking the same station,
    but using a different climatology.
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station1",
            default="IATDSM",
            label="Select First Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="c1",
            label="Climatology Source for First Station:",
            default="1951",
            options=PDICT,
        ),
        dict(
            type="station",
            name="station2",
            default="IATDSM",
            optional=True,
            label="Select Second Station (Optional):",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="c2",
            label="Climatology Source for Second Station:",
            default="1951",
            options=PDICT,
        ),
        dict(
            type="select",
            name="s",
            label="For difference plot, should smoother be applied:",
            default="0",
            options=PDICT2,
        ),
        dict(
            type="year",
            min=1880,
            name="sy1",
            default=1991,
            label="Inclusive Start Year for First Station Period of Years:",
        ),
        dict(
            type="year",
            min=1880,
            name="ey1",
            default=2020,
            label="Inclusive End Year for First Station Period of Years:",
        ),
        dict(
            type="year",
            min=1880,
            name="sy2",
            default=1981,
            label="Inclusive Start Year for Second Station Period of Years:",
        ),
        dict(
            type="year",
            min=1880,
            name="ey2",
            default=2010,
            label="Inclusive End Year for Second Station Period of Years:",
        ),
    ]
    return desc


def pick_climate(ctx, idx):
    """Figure out what we need to use."""
    climo = ctx.get(f"c{idx}", "1951")
    cltable = "climate"
    clstation = ctx.get(f"station{idx}")
    if climo == "1951":
        cltable = "climate51"
        clstation = ctx.get(f"station{idx}")
    elif climo == "ncei81":
        cltable = "ncdc_climate81"
        if clstation in ctx[f"_nt{idx}"].sts:
            clstation = ctx[f"_nt{idx}"].sts[clstation]["ncdc81"]
    return cltable, clstation


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    station1 = ctx["station1"]
    station2 = ctx.get("station2")
    c1 = ctx["c1"]
    c2 = ctx.get("c2")

    dbconn = get_dbconn("coop")
    cltable1, clstation1 = pick_climate(ctx, "1")
    cltable2, clstation2 = pick_climate(ctx, "2")

    if c1 == "custom":
        df = read_sql(
            "SELECT sday, station, avg(high) as high, avg(low) as low "
            f"from alldata_{station1[:2]} WHERE "
            "station = %s and sday != '0229' and year >= %s and year <= %s "
            "and high is not null and "
            "low is not null GROUP by sday, station ORDER by sday ASC",
            dbconn,
            params=(station1, ctx["sy1"], ctx["ey1"]),
            index_col=None,
        )
        df["valid"] = pd.to_datetime(df["sday"] + "2000", format="%m%d%Y")
        df = df.set_index("valid")
    else:
        df = read_sql(
            f"SELECT valid, station, high, low from {cltable1} WHERE "
            "station = %s and valid != '2000-02-29' ORDER by valid ASC",
            dbconn,
            params=(clstation1,),
            index_col="valid",
        )
    if df.empty:
        raise NoDataFound("Failed to find data for station1")
    if station2:
        if c2 == "custom":
            df2 = read_sql(
                "SELECT sday, station, avg(high) as high, avg(low) as low "
                f"from alldata_{station2[:2]} WHERE "
                "station = %s and sday != '0229' and year >= %s and "
                "year <= %s and high is not null and "
                "low is not null GROUP by sday, station ORDER by sday ASC",
                dbconn,
                params=(station2, ctx["sy2"], ctx["ey2"]),
                index_col=None,
            )
            df2["valid"] = pd.to_datetime(
                df2["sday"] + "2000", format="%m%d%Y"
            )
            df2 = df2.set_index("valid")

        else:
            df2 = read_sql(
                f"SELECT valid, station, high, low from {cltable2} WHERE "
                "station = %s and valid != '2000-02-29' ORDER by valid ASC",
                dbconn,
                params=(clstation2,),
                index_col="valid",
            )
        if df2.empty:
            raise NoDataFound("Failed to find data for station2")
        df["station2"] = station2
        df["high2"] = df2["high"]
        df["low2"] = df2["low"]

    fig = plt.figure(figsize=TWITTER_RESOLUTION_INCH)

    if station2 is not None:
        ax0 = fig.add_axes([0.05, 0.15, 0.43, 0.75])
        ax1 = fig.add_axes([0.55, 0.15, 0.43, 0.75])
    else:
        ax0 = fig.add_axes([0.05, 0.15, 0.8, 0.75])
        ax1 = None

    c1label = c1
    if c1 == "custom":
        c1label = "[%s-%s]" % (ctx["sy1"], ctx["ey1"])
    c2label = c2
    if c2 == "custom":
        c2label = "[%s-%s]" % (ctx["sy2"], ctx["ey2"])
    ax0.plot(
        df.index.values,
        df["high"],
        color="r",
        linestyle="-",
        label="High %s (%s)" % (station1, c1label),
    )
    ax0.plot(
        df.index.values,
        df["low"],
        color="b",
        label="Low %s (%s)" % (station1, c1label),
    )
    ax0.set_ylabel(r"Temperature $^\circ\mathrm{F}$")
    title = "[%s] %s %s Daily Averages" % (
        station1,
        ctx["_nt1"].sts[station1]["name"],
        PDICT[c1] if c1 != "custom" else c1label,
    )
    subtitle = None
    if station2 is not None:
        if station1 == station2:
            title = "[%s] %s %s vs %s" % (
                station1,
                ctx["_nt1"].sts[station1]["name"],
                PDICT[c1] if c1 != "custom" else c1label,
                PDICT[c2] if c2 != "custom" else c2label,
            )
            label = f"{c1label} - {c2label}"
        else:
            title = "Daily Climatology Comparison"
            subtitle = "[%s] %s %s vs [%s] %s %s" % (
                station1,
                ctx["_nt1"].sts[station1]["name"],
                PDICT[ctx["c1"]],
                station2,
                ctx["_nt2"].sts[station2]["name"],
                PDICT[ctx["c2"]],
            )
            label = "%s (%s) - %s (%s)" % (station1, c1, station2, c2)
        ax0.plot(
            df.index.values,
            df["high2"],
            color="brown",
            label="High %s (%s)" % (station2, c2label),
        )
        ax0.plot(
            df.index.values,
            df["low2"],
            color="green",
            label="Low %s (%s)" % (station2, c2label),
        )
        delta = df["high"] - df["high2"]
        if ctx["s"] != "0":
            ax1.text(
                0.01,
                0.99,
                "%s Day Smoother Applied" % (int(ctx["s"]),),
                transform=ax1.transAxes,
                va="top",
            )
            delta = delta.rolling(window=int(ctx["s"])).mean()
        ax1.plot(
            df.index.values,
            delta.values,
            color="r",
            label=f"High Diff {label}",
        )
        delta = df["low"] - df["low2"]
        if ctx["s"] != "0":
            delta = delta.rolling(window=int(ctx["s"])).mean()
        ax1.plot(df.index.values, delta, color="b", label=f"Low Diff {label}")
        ax1.set_ylabel(r"Temp Difference $^\circ\mathrm{F}$")
        ax1.legend(ncol=1, loc="center", bbox_to_anchor=(0.5, -0.1))
        ax1.grid(True)
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    fitbox(fig, title, 0.05, 0.94, 0.95, 0.99)
    if subtitle is not None:
        fitbox(fig, subtitle, 0.05, 0.95, 0.905, 0.935)
    ax0.legend(fontsize=10, ncol=2, loc="center", bbox_to_anchor=(0.5, -0.1))
    ax0.grid()
    ax0.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax0.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    return fig, df


if __name__ == "__main__":
    plotter(
        dict(
            network1="IACLIMATE",
            station1="IA0112",
            c1="custom",
            network2="IACLIMATE",
            station2="IA0112",
            c2="por",
            s="0",
            sy1=1981,
            ey1=2010,
            sy2=1991,
            ey2=2020,
        )
    )
