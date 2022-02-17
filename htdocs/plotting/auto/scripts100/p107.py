"""COOP period stats"""
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
    "precip": "Total Precipitation",
    "snow": "Total Snowfall",
    "days-snow-above": (
        "Days with Snowfall Greater Than or Equal To (threshold)"
    ),
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents statistics for a period of
    days each year provided your start date and number of days after that
    date. If your period crosses a year bounds, the plotted year represents
    the year of the start date of the period.

    <br /><br />This autoplot is specific to data from COOP stations, a
    similiar autoplot <a href="/plotting/auto/?q=140">#140</a> exists for
    automated stations.
    """
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
    ets = sts + datetime.timedelta(days=(days - 1))
    varname = ctx["varname"]
    year = ctx["year"]
    threshold = ctx["thres"]
    sdays = []
    for i in range(days):
        ts = sts + datetime.timedelta(days=i)
        sdays.append(ts.strftime("%m%d"))

    doff = (days + 1) if ets.year != sts.year else 0
    culler = " and snow is not null" if varname.find("snow") > -1 else ""
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
        SELECT extract(year from day - '{doff} days'::interval)::int as yr,
        avg((high+low)/2.) as avg_temp, avg(high) as avg_high_temp,
        sum(gddxx(:gddbase, :gddceil, high, low)) as gdd,
        avg(low) as avg_low_temp,
        sum(precip) as precip,
        sum(snow) as snow,
        min(low) as min_low,
        max(low) as max_low,
        max(high) as max_high,
        min(high) as min_high,
        sum(case when high >= :t then 1 else 0 end) as "days-high-above",
        sum(case when high < :t then 1 else 0 end) as "days-high-below",
        sum(case when low >= :t then 1 else 0 end) as "days-lows-above",
        sum(case when low < :t then 1 else 0 end) as "days-lows-below",
        sum(case when snow >= :t then 1 else 0 end) as "days-snow-above",
        count(*)
        from alldata_{station[:2]} WHERE station = :station and sday in :sdays
        {culler} GROUP by yr ORDER by yr ASC
        """
            ),
            conn,
            params={
                "gddbase": gddbase,
                "gddceil": gddceil,
                "t": threshold,
                "station": station,
                "sdays": tuple(sdays),
            },
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    fmter = intfmt if varname.find("days") > -1 else nice
    yrfmter = intfmt if sts.year == ets.year else crossesjan1
    df["range_high"] = df["max_high"] - df["min_high"]
    df["range_low"] = df["max_low"] - df["min_low"]
    # require at least 90% coverage
    df = df[df["count"] >= (days * 0.9)]
    # require values , not nan
    df = df[df[varname].notnull()].sort_values(varname, ascending=False)

    title = PDICT.get(varname).replace("(threshold)", str(threshold))
    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']}\n"
        f"{title} from {sts:%-d %B} through {ets:%-d %B}"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1)
    # Move axes over to make some room for the top 10
    ax[0].set_position([0.07, 0.53, 0.78, 0.36])
    ax[1].set_position([0.07, 0.1, 0.78, 0.36])

    # Print top 10
    dy = 0.03
    ypos = 0.9
    fig.text(0.86, ypos, "Top 10")
    for _, row in df.head(10).iterrows():
        ypos -= dy
        _fp = {"weight": "bold"} if row["yr"] == year else {}
        fig.text(0.86, ypos, yrfmter(row["yr"]), font_properties=_fp)
        fig.text(0.95, ypos, fmter(row[varname]), font_properties=_fp)

    ypos -= 2 * dy
    fig.text(0.86, ypos, "Bottom 10")
    ypos = ypos - 10 * dy
    for _, row in df.tail(10).iterrows():
        _fp = {"weight": "bold"} if row["yr"] == year else {}
        fig.text(0.86, ypos, yrfmter(row["yr"]), font_properties=_fp)
        fig.text(0.95, ypos, fmter(row[varname]), font_properties=_fp)
        ypos += dy

    bars = ax[0].bar(df["yr"], df[varname], facecolor="r", edgecolor="r")
    thisvalue = "M"
    for mybar, x, y in zip(bars, df["yr"], df[varname]):
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
    elif varname.find("days") > -1:
        ylabel = "Days"
    elif varname == "gdd":
        ylabel = f"Growing Degree Days ({gddbase},{gddceil}) " r"$^\circ$F"
    ax[0].set_ylabel(ylabel)
    ax[0].grid(True)
    ax[0].legend(ncol=2, fontsize=10)
    ax[0].set_xlim(df["yr"].min() - 1, df["yr"].max() + 1)
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
        f"Min: {df2[varname].min():.2f} {yrfmter(df['yr'][mysort.index[0]])}\n"
        f"95th: {ptile[1]:.2f}\n"
        f"Mean: {np.average(df2[varname]):.2f}\n"
        f"STD: {np.std(df2[varname]):.2f}\n"
        f"5th: {ptile[3]:.2f}\n"
        f"Max: {df2[varname].max():.2f} {yrfmter(df['yr'][mysort.index[-1]])}"
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
    plotter({"varname": "days-snow-above", "thres": 0.01})
