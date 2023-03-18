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
"""
import datetime

import numpy as np
import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from sqlalchemy import text

PDICT = {
    "avg_high_temp": "Average High Temperature",
    "avg_low_temp": "Average Low Temperature",
    "avg_temp": "Average Temperature",
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
    "avg_era5land_srad": "Average Daily Solar Radiation (ERA5 Land)",
    "max_era5land_srad": "Max Daily Solar Radiation (ERA5 Land)",
    "min_era5land_srad": "Min Daily Solar Radiation (ERA5 Land)",
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
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(
            type="month",
            name="month",
            default=(today - datetime.timedelta(days=14)).month,
            label="Start Month:",
        ),
        dict(
            type="day",
            name="day",
            default=(today - datetime.timedelta(days=14)).day,
            label="Start Day:",
        ),
        dict(type="int", name="days", default="14", label="Number of Days"),
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
    days = ctx["days"]
    gddbase = ctx["base"]
    gddceil = ctx["ceil"]
    sts = datetime.date(2012, ctx["month"], ctx["day"])
    ets = sts + datetime.timedelta(days=days - 1)
    varname = ctx["varname"]
    year = ctx["year"]
    threshold = ctx["thres"]
    stop = ctx.get("stop")
    params = {
        "gddbase": gddbase,
        "gddceil": gddceil,
        "t": threshold,
        "station": station,
    }
    if stop is None:
        sdays = []
        for i in range(days):
            ts = sts + datetime.timedelta(days=i)
            sdays.append(ts.strftime("%m%d"))
        daylimit = "sday in :sdays"
        params["sdays"] = tuple(sdays)
        doff = (days + 1) if ets.year != sts.year else 0
    else:
        daylimit = "sday >= :sday"
        params["sday"] = sts.strftime("%m%d")
        doff = 0
    culler = ""
    if varname.find("snow") > -1:
        culler = " and snow is not null"
    elif varname.find("era5") > -1:
        culler = " and era5land_srad is not null"

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
        SELECT extract(year from day - '{doff} days'::interval)::int as yr,
        day, high, low, precip, snow, (high + low) / 2. as avg_temp,
        gddxx(:gddbase, :gddceil, high, low) as gdd, era5land_srad
        from alldata WHERE station = :station and {daylimit}
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
            avg_era5land_srad=("era5land_srad", "mean"),
            min_era5land_srad=("era5land_srad", "min"),
            max_era5land_srad=("era5land_srad", "max"),
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
    yrfmter = intfmt if sts.year == ets.year else crossesjan1
    if stop is None:
        # require at least 90% coverage
        df = df[df["count"] >= (days * 0.9)]
    else:
        # Drop last row
        df = df.iloc[:-1]
        # drop any rows with a min date not equal to sts
        df = df[df["min_day"].dt.strftime("%m%d") == sts.strftime("%m%d")]
    # require values , not nan
    df2 = df[df[varname].notnull()].sort_values(varname, ascending=False)

    title = PDICT.get(varname).replace("(threshold)", str(threshold))
    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']}\n"
        f"{title} from {sts:%-d %B} "
    )
    if stop is None:
        title += f"through {ets:%-d %B}"
    else:
        title += f"until first day after 1 July w/ Low < {stop}F"
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1)
    # Move axes over to make some room for the top 10
    ax[0].set_position([0.07, 0.53, 0.78, 0.36])
    ax[1].set_position([0.07, 0.1, 0.78, 0.36])

    # Print top 10
    dy = 0.03
    ypos = 0.9
    fig.text(0.86, ypos, "Top 10")
    for yr, row in df2.head(10).iterrows():
        ypos -= dy
        _fp = {"weight": "bold"} if yr == year else {}
        fig.text(0.86, ypos, yrfmter(yr), font_properties=_fp)
        fig.text(0.95, ypos, fmter(row[varname]), font_properties=_fp)

    ypos -= 2 * dy
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
    plotter({"varname": "snow", "thres": 0.01, "stop": 32})
