"""
This plot presents a daily time series of variable of your choice.
The average temperature is simply the
average of the daily high and low.  The daily climatology is simply based
on the period of record observations for the site.

<p><strong>Updated 30 Jan 2024:</strong> The returned data is now only for the
variable you selected for plotting.
"""

import datetime

import matplotlib.colors as mpcolors
import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes, get_cmap
from pyiem.util import get_autoplot_context
from sqlalchemy import text

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.barchart import barchar_with_top10

PDICT = {
    "avg": "Daily Average Temperature (F)",
    "gdd": "Growing Degree Days (F)",
    "high": "High Temperature (F)",
    "low": "Low Temperature (F)",
    "era5land_soilm4_avg": "ERA5-Land 0-7cm Soil Moisture (m3/m3)",
    "era5land_soilm1m_avg": "ERA5-Land 0-1m Soil Moisture (m3/m3)",
    "era5land_soilm1m_sw": "ERA5-Land 0-39inch Soil Water Depth (inch)",
    "era5land_soilt4_avg": "ERA5-Land 0-7cm Soil Temperature (F)",
    "era5land_srad": "ERA5-Land Solar Radiation (MJ/m2)",
    "power_srad": "NASA POWER Solar Radiation (MJ/m2)",
}
OPTDICT = {
    "diff": "Absolute Difference",
    "sigma": "Difference in Standard Deviations",
    "ptile": "Percentile",
    "valrange": "Value within Observed Range",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="year",
            name="year",
            default=datetime.date.today().year,
            label="Year to Plot:",
        ),
        dict(
            type="select",
            name="var",
            default="high",
            options=PDICT,
            label="Select Variable to Plot",
        ),
        dict(
            type="int",
            name="gddbase",
            default=50,
            label="Growing Degree Day Base (F)",
        ),
        dict(
            type="int",
            name="gddceil",
            default=86,
            label="Growing Degree Day Ceiling (F)",
        ),
        dict(
            type="select",
            name="how",
            default="diff",
            options=OPTDICT,
            label="How to express the difference",
        ),
        dict(
            type="cmap",
            name="cmap",
            default="jet",
            label="Color ramp to use for percentile plot",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    year = ctx["year"]
    varname = ctx["var"]
    how = ctx["how"]
    gddbase = ctx["gddbase"]
    gddceil = ctx["gddceil"]

    params = {
        "station": station,
        "gddbase": gddbase,
        "gddceil": gddceil,
    }
    sqlvarname = "high" if varname in ["avg", "gdd"] else varname
    if varname == "era5land_soilm1m_sw":
        sqlvarname = "era5land_soilm1m_avg"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
            select day, year, sday,
            (high+low)/2. as avg,
            gddxx(:gddbase, :gddceil, high, low) as gdd, {sqlvarname}
            from alldata where station = :station and
            {sqlvarname} is not null ORDER by day ASC
        """
            ),
            conn,
            params=params,
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    if varname == "era5land_soilm1m_sw":
        df[varname] = df["era5land_soilm1m_avg"] * 39.3701
    # Compute the ranks of the daily values by sday
    df["rank"] = df.groupby("sday")[varname].rank(method="min")
    thisyear = (
        df[df["year"] == year]
        .set_index("sday")
        .copy()
        .reindex(
            pd.date_range(f"{year}/1/1", f"{year}/12/31").strftime("%m%d")
        )
        .assign(
            day=lambda x: pd.date_range(f"{year}/1/1", f"{year}/12/31").values
        )
    )
    if thisyear[varname].isna().all():
        raise NoDataFound("No Data Found.")
    thisyear.index.name = "MonDay"
    thisyear[f"{varname}_ptile"] = thisyear["rank"] / df["rank"].max() * 100.0
    climo = (
        df[["sday", varname]]
        .groupby("sday")
        .agg(["mean", "std", "min", "max"])
    )
    climo.columns = climo.columns.droplevel()
    thisyear[f"{varname}_mean"] = climo["mean"]
    thisyear[f"{varname}_min"] = climo["min"]
    thisyear[f"{varname}_max"] = climo["max"]
    thisyear[f"{varname}_std"] = climo["std"]
    thisyear[f"{varname}_range"] = climo["max"] - climo["min"]
    thisyear[f"{varname}_diff"] = thisyear[varname] - climo["mean"]
    thisyear[f"{varname}_sigma"] = thisyear[f"{varname}_diff"] / climo["std"]

    tt = "Departure" if how != "ptile" else "Percentile"
    if how == "valrange":
        tt = ""
    title = f"{ctx['_sname']}:: Year {year} Daily {PDICT[varname]} {tt}"
    subtitle = (
        f"{year} data till "
        f"{thisyear.loc[thisyear[varname].notna(), 'day'].max():%-d %b %Y}"
    )
    if varname.startswith("era5land_soilm"):
        slt = ctx["_nt"].sts[station]["attributes"].get("ERA5LAND_SOILTYPE")
        subtitle += f", ERA5-Land Soil Type: {slt}"
    (fig, ax) = figure_axes(apctx=ctx, title=title, subtitle=subtitle)
    if how == "valrange":
        ax.bar(
            thisyear["day"].values,
            thisyear[f"{varname}_range"].values,
            bottom=thisyear[f"{varname}_min"].values,
            color="tan",
            width=1.0,
            label=f"Observed Range {df.iloc[0]['year']}-{df.iloc[-1]['year']}",
        )
        ax.bar(
            thisyear["day"].values,
            thisyear[f"{varname}_std"].values * 2.0,
            bottom=(
                thisyear[f"{varname}_mean"].values
                - thisyear[f"{varname}_std"].values
            ),
            color="green",
            width=1.0,
            label="+/- 1 Std Dev",
        )
        ax.plot(
            thisyear["day"].values,
            thisyear[varname].values,
            color="k",
            label=str(year),
        )
        ax.plot(
            thisyear["day"].values,
            thisyear[f"{varname}_mean"].values,
            color="r",
            label="Climatology",
        )
        ax.legend(loc="best", ncol=4)
    else:
        values = thisyear[f"{varname}_{how}"].values
        if how == "ptile" and "cmap" in ctx:
            bins = range(0, 101, 10)
            cmap = get_cmap(ctx["cmap"])
            norm = mpcolors.BoundaryNorm(bins, cmap.N)
            colors = cmap(norm(values))
            ax.bar(
                thisyear["day"].values, values, color=colors, align="center"
            )
            ax.set_yticks(bins)
        else:
            abovecolor = "r" if how == "diff" else "b"
            belowcolor = "b" if how == "diff" else "r"
            if varname.find("soilm") > 0:
                abovecolor = "b"
                belowcolor = "r"
            thisyear["color"] = abovecolor
            thisyear.loc[values < 0, "color"] = belowcolor
            ax.set_position([0.1, 0.1, 0.7, 0.8])
            ax = barchar_with_top10(
                fig,
                thisyear.rename(columns={f"{varname}_{how}": "Diff"}),
                "Diff",
                ax=ax,
                color=thisyear["color"].values,
            )
            meanval = thisyear[f"{varname}_mean"].mean()
            ax.text(
                0.99,
                1.01,
                f"Mean: {meanval:.1f}",
                transform=ax.transAxes,
                color="k",
                ha="right",
                va="bottom",
                bbox=dict(facecolor="white", edgecolor="white"),
            )

            ax.text(
                0.9,
                0.95,
                f"Days Above {(values > 0).sum()}",
                transform=ax.transAxes,
                color=abovecolor,
                ha="center",
                va="top",
                bbox=dict(facecolor="white", edgecolor="white"),
            )
            ax.text(
                0.9,
                0.05,
                f"Days Below {(values < 0).sum()}",
                transform=ax.transAxes,
                color=belowcolor,
                ha="center",
                va="top",
                bbox=dict(facecolor="white", edgecolor="white"),
            )
    if how == "diff":
        ax.set_ylabel(f"{PDICT[varname]} Departure")
    elif how == "ptile":
        ax.set_ylabel(f"{PDICT[varname]} Percentile (100 highest)")
    elif how == "valrange":
        ax.set_ylabel(PDICT[varname])
    else:
        ax.set_ylabel(f"{PDICT[varname]} Std Dev Departure")
    if varname == "gdd":
        ax.set_xlabel(f"Growing Degree Day Base: {gddbase} Ceiling: {gddceil}")
    ax.grid(True)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.set_major_locator(mdates.DayLocator(1))

    return fig, thisyear
