"""
This plot presents aggregate statistics by year for a date period
of your choice.  You can either set an explicit date period or make
the end date based on the first date below a given low temperature
threshold. If your period crosses a year bounds,
the plotted year represents the year of the start date of the period.

<br /><br />This autoplot is specific to data from COOP stations, a
similiar autoplot <a href="/plotting/auto/?q=140">#140</a> exists for
automated stations.

<p>A quorum of at least 90% of the days within the choosen period must have
data in order to be included within the plot.

<p><strong>Updated 12 Oct 2023:</strong> The API for this autoplot was changed
to use a more user friendly start and end date.
"""

import datetime

import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context
from sqlalchemy import text

PDICT = {
    "avg_high_temp": "Average High Temperature",
    "avg_low_temp": "Average Low Temperature",
    "avg_temp": "Average Temperature",
    "avg_range": "Average Daily Temperature Range",
    "gdd": "Growing Degree Days",
    "days-high-above": (
        "Days with High Temp Greater Than or Equal To (threshold)"
    ),
    "days-high-below": "Days with High Temp Below (threshold)",
    "days-lows-above": (
        "Days with Low Temp Greater Than or Equal To (threshold)"
    ),
    "days-lows-below": "Days with Low Temp Below (threshold)",
    "max_high": "Maximum High Temperature",
    "min_high": "Minimum High Temperature",
    "range_high": "Range of High Temperature",
    "min_low": "Minimum Low Temperature",
    "max_low": "Maximum Low Temperature",
    "range_low": "Range of Low Temperature",
    "avg_era5land_soilt4_avg": "Avg Daily Soil (0-7cm) Temp (ERA5-Land)",
    "avg_era5land_soilm1m_avg": "Avg Daily Soil (0-1m) Moisture (ERA5-Land)",
    "avg_era5land_srad": "Average Daily Solar Radiation (ERA5-Land)",
    "max_era5land_srad": "Max Daily Solar Radiation (ERA5-Land)",
    "min_era5land_srad": "Min Daily Solar Radiation (ERA5-Land)",
    "avg_merra_srad": "Average Daily Solar Radiation (MERRAv2)",
    "max_merra_srad": "Max Daily Solar Radiation (MERRAv2)",
    "min_merra_srad": "Min Daily Solar Radiation (MERRAv2)",
    "avg_narr_srad": "Average Daily Solar Radiation (NARR)",
    "max_narr_srad": "Max Daily Solar Radiation (NARR)",
    "min_narr_srad": "Min Daily Solar Radiation (NARR)",
    "precip": "Total Precipitation",
    "snow": "Total Snowfall",
    "days-precip-above": (
        "Days with Precipitation Greater Than or Equal To (threshold)"
    ),
    "days-snow-above": (
        "Days with Snowfall Greater Than or Equal To (threshold)"
    ),
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    sts = today - datetime.timedelta(days=14)
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        ),
        {
            "type": "sday",
            "name": "sday",
            "default": f"{sts:%m%d}",
            "label": "Inclusive Start Date of the Year",
        },
        {
            "type": "sday",
            "name": "eday",
            "default": f"{today:%m%d}",
            "label": "Inclusise End Date of the Year",
        },
        dict(
            optional=True,
            type="int",
            name="stop",
            default="32",
            label=(
                "Stop accumulation once daily low (after 1 July) "
                "below threshold (F) [overrides number of days above]"
            ),
        ),
        dict(
            type="select",
            name="varname",
            default="avg_temp",
            label="Variable to Compute:",
            options=PDICT,
        ),
        dict(
            type="float",
            name="thres",
            default=-99,
            label="Threshold (when appropriate):",
        ),
        dict(
            type="int",
            name="base",
            default=50,
            label="Growing Degree Day Base (F)",
        ),
        dict(
            type="int",
            name="ceil",
            default=86,
            label="Growing Degree Day Ceiling (F)",
        ),
        dict(
            type="year",
            name="year",
            default=today.year,
            label="Year to Highlight in Chart:",
        ),
    ]
    return desc


def crossesjan1(val):
    """Pretty print for a year."""
    return f"{val:.0f}-{(val + 1):.0f}"


def intfmt(val):
    """format int values"""
    if val == "M":
        return "M"
    return f"{val:.0f}"


def nice(val):
    """nice printer"""
    if val == "M":
        return "M"
    if 0 < val < 0.01:
        return "Trace"
    return f"{val:.2f}"


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    gddbase = ctx["base"]
    gddceil = ctx["ceil"]
    varname = ctx["varname"]
    year = ctx["year"]
    threshold = ctx["thres"]
    stop = ctx.get("stop")
    params = {
        "gddbase": gddbase,
        "gddceil": gddceil,
        "t": threshold,
        "station": station,
        "sday": ctx["sday"].strftime("%m%d"),
        "eday": ctx["eday"].strftime("%m%d"),
    }
    dtlimiter = "(sday >= :sday and sday <= :eday)"
    doff = "year"
    if ctx["eday"] < ctx["sday"]:
        dtlimiter = "(sday >= :sday or sday <= :eday)"
        doff = "case when sday <= :eday then year - 1 else year end"
    if stop is not None:
        dtlimiter = "sday >= :sday"
        doff = "year"
    culler = ""
    if varname.find("snow") > -1:
        culler = " and snow is not null"
    elif varname.find("era5land_srad") > -1:
        culler = " and era5land_srad is not null"
    elif varname.find("era5land_soilt4") > -1:
        culler = " and era5land_soilt4_avg is not null"
    elif varname.find("era5land_soilm1m") > -1:
        culler = " and era5land_soilm1m_avg is not null"
    elif varname.find("merra") > -1:
        culler = " and merra_srad is not null"
    elif varname.find("narr") > -1:
        culler = " and narr_srad is not null"

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
        SELECT {doff} as yr,
        day, high, low, precip, snow, (high + low) / 2. as avg_temp,
        high - low as range,
        gddxx(:gddbase, :gddceil, high, low) as gdd, era5land_srad,
        era5land_soilt4_avg, era5land_soilm1m_avg,
        merra_srad, narr_srad
        from alldata WHERE station = :station and {dtlimiter}
        {culler} ORDER by day ASC
        """
            ),
            conn,
            params=params,
            index_col=None,
            parse_dates="day",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    if stop is not None:
        # Compute the first date each year with the low below stop treshold
        # and truncate the dataframe to that date.
        df = (
            df.assign(
                hit=lambda df_: (
                    (df_["day"].dt.month >= 7) & (df_["low"] < stop)
                )
            )
            .groupby("yr")
            .apply(
                lambda g: (
                    g
                    if not g["hit"].any()
                    else g.loc[: g.low[g["hit"]].index[0]]
                )
            )
            .transform(lambda g: g)
            .reset_index(drop=True)
            .set_index("day")
        )

    # Now we compute the aggregates for each year.
    df = (
        df.reset_index()
        .groupby("yr")
        .agg(
            avg_temp=("avg_temp", "mean"),
            avg_high_temp=("high", "mean"),
            avg_low_temp=("low", "mean"),
            avg_range=("range", "mean"),
            precip=("precip", "sum"),
            snow=("snow", "sum"),
            gdd=("gdd", "sum"),
            min_low=("low", "min"),
            max_low=("low", "max"),
            max_high=("high", "max"),
            min_high=("high", "min"),
            days_high_above=("high", lambda x: (x >= threshold).sum()),
            days_high_below=("high", lambda x: (x < threshold).sum()),
            days_lows_above=("low", lambda x: (x >= threshold).sum()),
            days_lows_below=("low", lambda x: (x < threshold).sum()),
            days_snow_above=("snow", lambda x: (x >= threshold).sum()),
            days_precip_above=("precip", lambda x: (x >= threshold).sum()),
            count=("high", "count"),
            min_day=("day", "min"),
            avg_era5land_soilt4_avg=("era5land_soilt4_avg", "mean"),
            avg_era5land_soilm1m_avg=("era5land_soilm1m_avg", "mean"),
            avg_era5land_srad=("era5land_srad", "mean"),
            min_era5land_srad=("era5land_srad", "min"),
            max_era5land_srad=("era5land_srad", "max"),
            avg_merra_srad=("merra_srad", "mean"),
            min_merra_srad=("merra_srad", "min"),
            max_merra_srad=("merra_srad", "max"),
            avg_narr_srad=("narr_srad", "mean"),
            min_narr_srad=("narr_srad", "min"),
            max_narr_srad=("narr_srad", "max"),
        )
        .reset_index()
        .rename(
            columns={
                "days_high_above": "days-high-above",
                "days_high_below": "days-high-below",
                "days_lows_above": "days-lows-above",
                "days_lows_below": "days-lows-below",
                "days_snow_above": "days-snow-above",
                "days_precip_above": "days-precip-above",
            }
        )
        .set_index("yr")
        .assign(
            range_high=lambda df_: df_["max_high"] - df_["min_high"],
            range_low=lambda df_: df_["max_low"] - df_["min_low"],
        )
    )

    fmter = intfmt if varname.find("days") > -1 else nice
    if varname in ["min_low", "max_low", "min_high", "max_high"]:
        fmter = intfmt
    yrfmter = intfmt if ctx["eday"] > ctx["sday"] else crossesjan1
    if stop is None:
        # require at least 90% coverage
        df = df[df["count"] >= (df["count"].max() * 0.9)]
    else:
        # Drop last row
        df = df.iloc[:-1]
        # drop any rows with a min date not equal to sts
        mm = ctx["sday"].strftime("%m%d")
        df = df[df["min_day"].dt.strftime("%m%d") == mm]
    # require values , not nan
    df2 = df[df[varname].notnull()].sort_values(varname, ascending=False)

    title = PDICT[varname].replace("(threshold)", str(threshold))
    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']}\n"
        f"{title} from {ctx['sday']:%-d %B} "
    )
    if stop is None:
        title += f"through {ctx['eday']:%-d %B}"
    else:
        title += f"until first day after 1 July w/ Low < {stop}F"
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1)
    # Move axes over to make some room for the top 10
    ax[0].set_position([0.07, 0.53, 0.78, 0.36])
    ax[1].set_position([0.07, 0.1, 0.78, 0.36])

    # Print top 10
    dy = 0.03
    ypos = 0.88
    fig.text(0.86, ypos, "Top 10")
    for yr, row in df2.head(10).iterrows():
        ypos -= dy
        _fp = {"weight": "bold"} if yr == year else {}
        fig.text(0.86, ypos, yrfmter(yr), font_properties=_fp)
        fig.text(0.95, ypos, fmter(row[varname]), font_properties=_fp)

    ypos -= 4 * dy
    fig.text(0.86, ypos, "Bottom 10")
    ypos = ypos - 10 * dy
    for yr, row in df2.tail(10).iterrows():
        _fp = {"weight": "bold"} if yr == year else {}
        fig.text(0.86, ypos, yrfmter(yr), font_properties=_fp)
        fig.text(0.95, ypos, fmter(row[varname]), font_properties=_fp)
        ypos += dy

    bars = ax[0].bar(df.index, df[varname], facecolor="r", edgecolor="r")
    thisvalue = "M"
    for mybar, x, y in zip(bars, df.index, df[varname]):
        if x == year:
            mybar.set_facecolor("g")
            mybar.set_edgecolor("g")
            thisvalue = y
    ax[0].set_xlabel(f"Year, {yrfmter(year)} = {fmter(thisvalue)}")
    ax[0].axhline(
        df[varname].mean(), lw=2, label=f"Avg: {df[varname].mean():.2f}"
    )
    ylabel = r"Temperature $^\circ$F"
    if varname in ["precip"]:
        ylabel = "Precipitation [inch]"
    elif varname in ["snow"]:
        ylabel = "Snowfall [inch]"
    elif varname.find("srad") > -1:
        vv = PDICT[varname].replace("Daily", "Daily\n")
        ylabel = f"{vv} [MJ/d]"
    elif varname.find("days") > -1:
        ylabel = "Days"
    elif varname == "gdd":
        ylabel = f"Growing Degree Days ({gddbase},{gddceil}) " r"$^\circ$F"
    elif varname.find("soilm") > -1:
        ylabel = "Soil Moisture $kg/kg$"
    ax[0].set_ylabel(ylabel)
    ax[0].grid(True)
    ax[0].legend(ncol=2, fontsize=10)
    ax[0].set_xlim(df.index[0] - 1, df.index[-1] + 1)
    rng = df[varname].max() - df[varname].min()
    if varname in ["snow", "precip"] or varname.startswith("days"):
        ax[0].set_ylim(-0.1, df[varname].max() + rng * 0.3)
    else:
        ax[0].set_ylim(
            df[varname].min() - rng * 0.3, df[varname].max() + rng * 0.3
        )
    box = ax[0].get_position()
    ax[0].set_position([box.x0, box.y0 + 0.02, box.width, box.height * 0.98])
    # Ensure that the x-axis labels are integer values
    ax[0].xaxis.set_major_locator(MaxNLocator(10, integer=True))

    # Plot 2: CDF
    df2 = df[df[varname].notnull()]
    X2 = np.sort(df2[varname])
    ptile = np.percentile(df2[varname], [0, 5, 50, 95, 100])
    N = len(df2[varname])
    F2 = np.array(range(N)) / float(N) * 100.0
    ax[1].plot(X2, 100.0 - F2)
    ax[1].set_xlabel(ylabel)
    ax[1].set_ylabel("Observed Frequency [%]")
    ax[1].grid(True)
    ax[1].set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    if thisvalue != "M":
        ax[1].axvline(thisvalue, color="g")
    mysort = df.sort_values(by=varname, ascending=True)
    info = (
        f"Min: {df2[varname].min():.2f} {yrfmter(mysort.index[0])}\n"
        f"95th: {ptile[1]:.2f}\n"
        f"Mean: {np.average(df2[varname]):.2f}\n"
        f"STD: {np.std(df2[varname]):.2f}\n"
        f"5th: {ptile[3]:.2f}\n"
        f"Max: {df2[varname].max():.2f} {yrfmter(mysort.index[-1])}"
    )
    ax[1].text(
        0.75,
        0.95,
        info,
        transform=ax[1].transAxes,
        va="top",
        bbox=dict(facecolor="white", edgecolor="k"),
    )
    return fig, df


if __name__ == "__main__":
    plotter({})
