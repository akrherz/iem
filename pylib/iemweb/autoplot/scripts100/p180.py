"""
This application plots daily climatology for
a location or two of your choice.  You can pick which climatology to use
and effectively build a difference plot when picking the same station,
but using a different climatology.
"""

import calendar

import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure, fitbox
from pyiem.util import get_autoplot_context

PDICT = {
    "por": "Period of Record (por) Climatology",
    "1951": "1951-present Climatology",
    "ncei81": "NCEI 1981-2010 Climatology",
    "ncei91": "NCEI 1991-2020 Climatology",
    "custom": "Custom Climatology (pick years)",
}
PDICT2 = {
    "0": "No Smoothing Applied",
    "7": "Seven Day Centered Smooth",
    "14": "Fourteen Day Centered Smooth",
}
PDICT3 = {
    "temps": "Plot High and Low Temperatures",
    "precip": "Precipitation",
    "snow": "Snowfall",
}
LABELS = {
    "temps": r"Temperature $^\circ\mathrm{F}$",
    "precip": "Precipitation [inch/day]",
    "snow": "Snowfall [inch/day]",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
    desc["data"] = True
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT3,
            default="temps",
            name="v",
            label="Which Variable(s) to Plot",
        ),
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
    elif climo == "ncei91":
        cltable = "ncei_climate91"
        if clstation in ctx[f"_nt{idx}"].sts:
            clstation = ctx[f"_nt{idx}"].sts[clstation]["ncei91"]
    return cltable, clstation


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    varname = ctx["v"]
    station1 = ctx["station1"]
    station2 = ctx.get("station2")
    c1 = ctx["c1"]
    c2 = ctx.get("c2")

    cltable1, clstation1 = pick_climate(ctx, "1")

    if c1 == "custom":
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                "SELECT sday, station, avg(high) as high, avg(low) as low, "
                "avg(precip) as precip, avg(snow) as snow "
                "from alldata WHERE "
                "station = %s and sday != '0229' and year >= %s and "
                "year <= %s and high is not null and "
                "low is not null GROUP by sday, station ORDER by sday ASC",
                conn,
                params=(station1, ctx["sy1"], ctx["ey1"]),
                index_col=None,
            )
        df["valid"] = pd.to_datetime(df["sday"] + "2000", format="%m%d%Y")
        df = df.set_index("valid")
    else:
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                "SELECT valid, station, high, low, precip, snow from "
                f"{cltable1} WHERE station = %s and valid != '2000-02-29' "
                "ORDER by valid ASC",
                conn,
                params=(clstation1,),
                parse_dates="valid",
                index_col="valid",
            )
    if df.empty:
        raise NoDataFound("Failed to find data for station1")
    if station2:
        cltable2, clstation2 = pick_climate(ctx, "2")
        if c2 == "custom":
            with get_sqlalchemy_conn("coop") as conn:
                df2 = pd.read_sql(
                    "SELECT sday, station, avg(high) as high, "
                    "avg(low) as low, avg(precip) as precip, "
                    "avg(snow) as snow from alldata WHERE "
                    "station = %s and sday != '0229' and year >= %s and "
                    "year <= %s and high is not null and "
                    "low is not null GROUP by sday, station ORDER by sday ASC",
                    conn,
                    params=(station2, ctx["sy2"], ctx["ey2"]),
                    index_col=None,
                )
            df2["valid"] = pd.to_datetime(
                df2["sday"] + "2000", format="%m%d%Y"
            )
            df2 = df2.set_index("valid")

        else:
            with get_sqlalchemy_conn("coop") as conn:
                df2 = pd.read_sql(
                    "SELECT valid, station, high, low, precip, snow from "
                    f"{cltable2} WHERE station = %s and valid != '2000-02-29' "
                    "ORDER by valid ASC",
                    conn,
                    params=(clstation2,),
                    parse_dates="valid",
                    index_col="valid",
                )
        if df2.empty:
            raise NoDataFound("Failed to find data for station2")
        df["station2"] = station2
        for v in ["high", "low", "precip", "snow"]:
            df[f"{v}2"] = df2[v]
            df[f"{v}diff"] = df[v] - df[f"{v}2"]

    fig = figure(apctx=ctx)

    ax1 = None
    ax2 = None
    if station2 is not None:
        ax0 = fig.add_axes([0.05, 0.15, 0.43, 0.75])
        ax1 = fig.add_axes([0.55, 0.55, 0.43, 0.35])
        ax2 = fig.add_axes([0.55, 0.07, 0.43, 0.35])
    else:
        ax0 = fig.add_axes([0.12, 0.15, 0.8, 0.75])

    c1label = c1
    if c1 == "custom":
        c1label = f"[{ctx['sy1']}-{ctx['ey1']}]"
    c2label = c2
    if c2 == "custom":
        c2label = f"[{ctx['sy2']}-{ctx['ey2']}]"
    var1 = "high" if varname == "temps" else varname
    var2 = "low" if varname == "temps" else None
    ax0.plot(
        df.index.values,
        df[var1],
        color="r",
        linestyle="-",
        label=f"{var1.capitalize()} {station1} ({c1label})",
    )
    if var2 is not None:
        ax0.plot(
            df.index.values,
            df[var2],
            color="b",
            label=f"Low {station1} ({c1label})",
        )
    ax0.set_ylabel(LABELS[varname])
    tt = PDICT[c1] if c1 != "custom" else c1label
    title = (
        f"[{station1}] {ctx['_nt1'].sts[station1]['name']}:: "
        f"{tt} Daily Averages"
    )
    subtitle = None
    if station2 is not None:
        if station1 == station2:
            title = (
                f"[{station1}] {ctx['_nt1'].sts[station1]['name']} "
                f"{PDICT[c1] if c1 != 'custom' else c1label} vs "
                f"{PDICT[c2] if c2 != 'custom' else c2label}"
            )
            label = f"{c1label} - {c2label}"
        else:
            title = "Daily Climatology Comparison"
            subtitle = (
                f"[{station1}] {ctx['_nt1'].sts[station1]['name']} "
                f"{PDICT[ctx['c1']]} vs [{station2}] "
                f"{ctx['_nt2'].sts[station2]['name']} {PDICT[ctx['c2']]}"
            )
            label = f"{station1} ({c1}) - {station2} ({c2})"
        ax0.plot(
            df.index.values,
            df[f"{var1}2"],
            color="brown" if var2 is not None else "blue",
            label=f"{var1.capitalize()} {station2} ({c2label})",
        )
        if var2 is not None:
            ax0.plot(
                df.index.values,
                df[f"{var2}2"],
                color="green",
                label=f"Low {station2} ({c2label})",
            )
        delta = df[f"{var1}diff"]
        if ctx["s"] != "0":
            ax1.text(
                0.01,
                0.99,
                f"** {int(ctx['s'])} Day Smoother Applied",
                transform=ax1.transAxes,
                va="top",
            )
            delta = delta.rolling(window=int(ctx["s"])).mean()
        ax1.plot(
            df.index.values,
            delta.values,
            color="r",
            label=f"{var1.capitalize()} Diff {label}",
        )
        if var2 is not None:
            delta = df["lowdiff"]
            if ctx["s"] != "0":
                delta = delta.rolling(window=int(ctx["s"])).mean()
            ax1.plot(
                df.index.values, delta, color="b", label=f"Low Diff {label}"
            )
        ax1.set_ylabel(f"{LABELS[varname]} Difference")
        ax1.legend(ncol=1, loc="center", bbox_to_anchor=(0.5, -0.2))
        ax1.grid()
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

        # Compute monthly
        gdf = df.groupby(df.index.month).mean(numeric_only=True)
        ax2.text(
            0.01,
            1.0,
            "Monthly Average Difference",
            transform=ax2.transAxes,
            va="bottom",
        )
        ax2.bar(
            gdf.index.values - (0.2 if var2 is not None else 0),
            gdf[f"{var1}diff"],
            width=0.4 if var2 is not None else 0.8,
            color="r",
        )
        if var2 is not None:
            ax2.bar(
                gdf.index.values + 0.2, gdf["lowdiff"], width=0.4, color="b"
            )
        ax2.set_ylabel(f"{LABELS[varname]} Difference")
        ax2.set_xticks(range(1, 13))
        ax2.set_xticklabels(calendar.month_abbr[1:])
        ax2.grid()

    fitbox(fig, title, 0.08, 0.94, 0.95, 0.99)
    if subtitle is not None:
        fitbox(fig, subtitle, 0.08, 0.95, 0.905, 0.935)
    ax0.legend(fontsize=10, ncol=2, loc="center", bbox_to_anchor=(0.5, -0.1))
    ax0.grid()
    ax0.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax0.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    return fig, df


if __name__ == "__main__":
    plotter({})
