"""
This plot presents statistics for a period of
days each year provided your start date and number of days after that
date. If your period crosses a year bounds, the plotted year represents
the year of the start date of the period. <strong>Average Dew Point Temp
</strong> is computed by averaging the daily max and min dew point values.

<br /><br />This autoplot is specific to data from automated stations, a
similiar autoplot <a href="/plotting/auto/?q=107">#107</a> exists for
long term COOP data.

<p><strong>Updated 27 Aug 2023:</strong> The API for this autoplot was changed
to use a more user friendly start and end date.
"""

import datetime

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

LOOKUP = {
    "avg_high_temp": "max_tmpf",
    "range_high_temp": "max_tmpf",
    "avg_low_temp": "min_tmpf",
    "range_low_temp": "min_tmpf",
    "avg_temp": "(max_tmpf + min_tmpf)/2.",
    "avg_dewp": "(max_dwpf + min_dwpf)/2.",
    "avg_wind_speed": "avg_sknt * 1.15",
    "max_high": "max_tmpf",
    "min_high": "max_tmpf",
    "max_low": "min_tmpf",
    "min_low": "min_tmpf",
    "precip": "pday",
}
PDICT = {
    "avg_high_temp": "Average High Temperature",
    "range_high_temp": "Range of High Temperature",
    "avg_low_temp": "Average Low Temperature",
    "range_low_temp": "Range of Low Temperature",
    "avg_temp": "Average Temperature",
    "avg_dewp": "Average Dew Point Temp",
    "avg_wind_speed": "Average Wind Speed",
    "max_high": "Maximum High Temperature",
    "min_high": "Minimum High Temperature",
    "max_low": "Maximum Low Temperature",
    "min_low": "Minimum Low Temperature",
    "max_feel": "Maximum Feels Like Temperature",
    "min_feel": "Minimum Feels Like Temperature",
    "max_rh": "Maximum Relative Humidity",
    "avg_rh": "Average Relative Humidity",
    "min_rh": "Minimum Relative Humidity",
    "precip": "Total Precipitation",
}
PDICT2 = {
    "none": "Plot metric, not count of days",
    "aoa": "Days At or Above Threshold",
    "below": "Days Below Threshold",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    sts = today - datetime.timedelta(days=14)
    desc["arguments"] = [
        dict(
            type="zstation",
            name="station",
            default="DSM",
            label="Select Station",
            network="IA_ASOS",
        ),
        dict(
            type="year",
            default=1928,
            min=1928,
            name="syear",
            label="Limit plot start year (if data exists) to:",
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
            type="select",
            name="varname",
            default="avg_temp",
            label="Variable to Compute:",
            options=PDICT,
        ),
        {
            "type": "select",
            "options": PDICT2,
            "name": "w",
            "default": "none",
            "label": "Use Threshold to Count Number of Days",
        },
        {
            "type": "float",
            "name": "thres",
            "label": "Threshold (inch, F, MPH, %)",
            "default": "1",
        },
        dict(
            type="year",
            name="year",
            default=sts.year,
            label="Year to Highlight in Chart:",
        ),
    ]
    return desc


def nice(val):
    """pretty print"""
    if val == "M":
        return "M"
    if 0 < val < 0.005:
        return "Trace"
    return f"{val:.2f}"


def crossesjan1(val):
    """Pretty print for a year."""
    return f"{val:.0f}-{(val + 1):.0f}"


def intfmt(val):
    """format int values"""
    if val == "M":
        return "M"
    return f"{val:.0f}"


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["varname"]
    year = ctx["year"]
    dtlimiter = (
        "(to_char(day, 'mmdd') >= :sday and to_char(day, 'mmdd') <= :eday)"
    )
    doff = "extract(year from day)"
    if ctx["eday"] < ctx["sday"]:
        dtlimiter = (
            "(to_char(day, 'mmdd') >= :sday or "
            "to_char(day, 'mmdd') <= :eday)"
        )
        doff = (
            "case when to_char(day, 'mmdd') <= :eday then "
            "(extract(year from day)::int - 1) else extract(year from day) end"
        )
    threshold = ctx["thres"]
    mydir = ">=" if ctx["w"] == "aoa" else "<"
    aggcol = LOOKUP.get(varname, varname)
    dfcol = ctx["varname"] if ctx["w"] == "none" else "count_days"
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            text(
                f"""
        SELECT {doff} as yr,
        avg((max_tmpf+min_tmpf)/2.) as avg_temp,
        avg(max_tmpf) as avg_high_temp,
        avg(min_tmpf) as avg_low_temp,
        sum(pday) as precip, avg(avg_sknt) * 1.15 as avg_wind_speed,
        min(min_tmpf) as min_low,
        max(min_tmpf) as max_low,
        max(max_tmpf) as max_high,
        min(max_tmpf) as min_high,
        max(max_rh) as max_rh,
        max(avg_rh) as avg_rh,
        min(min_rh) as min_rh,
        avg((max_dwpf + min_dwpf)/2.) as avg_dewp,
        max(max_feel) as max_feel, min(min_feel) as min_feel,
        sum(case when {aggcol} {mydir} {threshold} then 1 else 0 end) as
            count_days
        from summary s JOIN stations t on (s.iemid = t.iemid)
        WHERE t.network = :network and t.id = :station
        and {dtlimiter} and day >= :start
        GROUP by yr ORDER by yr ASC
        """
            ),
            conn,
            params={
                "network": ctx["network"],
                "station": station,
                "sday": f"{ctx['sday']:%m%d}",
                "eday": f"{ctx['eday']:%m%d}",
                "start": datetime.date(ctx["syear"], 1, 1),
            },
            index_col="yr",
        )
    if df.empty:
        raise NoDataFound("No data was found.")
    df["range_high_temp"] = df["max_high"] - df["min_high"]
    df["range_low_temp"] = df["max_low"] - df["min_low"]
    # require values , not nan
    df2 = df[df[dfcol].notnull()].sort_values(dfcol, ascending=False)

    ylabel = r"Temperature $^\circ$F"
    units = r"$^\circ$F"
    if varname in ["precip"]:
        ylabel = "Precipitation [inch]"
        units = "[inch]"
    elif varname in ["avg_wind_speed"]:
        ylabel = "Wind Speed [MPH]"
        units = "[MPH]"
    elif varname.find("rh") > -1:
        ylabel = "Relative Humidity [%]"
        units = "[%]"
    if ctx["w"] != "none":
        ylabel = "Days"
    title = (
        f"{ctx['_sname']}\n"
        f"{PDICT.get(varname)} from "
        f"{ctx['sday']:%d %b} through {ctx['eday']:%d %b}"
    )
    if ctx["w"] != "none":
        tt = PDICT2[ctx["w"]].replace("Threshold", f"{ctx['thres']}")
        title = (
            f"{ctx['_sname']}\n"
            f"{tt} {units} for {PDICT.get(varname)} "
            f"from {ctx['sday']:%d %b} through {ctx['eday']:%d %b}"
        )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1)
    ax[0].set_position([0.07, 0.53, 0.78, 0.36])
    ax[1].set_position([0.07, 0.1, 0.78, 0.36])

    fmter = intfmt if ctx["w"] != "none" else nice
    yrfmter = intfmt if ctx["eday"] > ctx["sday"] else crossesjan1

    # Print top 10
    dy = 0.03
    ypos = 0.9
    fig.text(0.86, ypos, "Top 10")
    for yr, row in df2.head(10).iterrows():
        ypos -= dy
        _fp = {"weight": "bold"} if yr == year else {}
        fig.text(0.86, ypos, yrfmter(yr), font_properties=_fp)
        fig.text(0.95, ypos, fmter(row[dfcol]), font_properties=_fp)

    ypos -= 2 * dy
    fig.text(0.86, ypos, "Bottom 10")
    ypos = ypos - 10 * dy
    for yr, row in df2.tail(10).iterrows():
        _fp = {"weight": "bold"} if yr == year else {}
        fig.text(0.86, ypos, yrfmter(yr), font_properties=_fp)
        fig.text(0.95, ypos, fmter(row[dfcol]), font_properties=_fp)
        ypos += dy

    bars = ax[0].bar(
        df.index, df[dfcol], facecolor="r", edgecolor="r", align="center"
    )
    thisvalue = "M"
    for mybar, x, y in zip(bars, df.index.values, df[dfcol]):
        if x == year:
            mybar.set_facecolor("g")
            mybar.set_edgecolor("g")
            thisvalue = y
    ax[0].set_xlabel(f"Year, {year} = {nice(thisvalue)}")
    ax[0].axhline(
        df[dfcol].mean(),
        lw=2,
        label=f"Avg: {df[dfcol].mean():.2f}",
        color="b",
    )
    trail = df[dfcol].rolling(30, min_periods=30, center=False).mean()
    ax[0].plot(trail.index, trail.values, color="k", label="30yr Avg", lw=2)
    ax[0].set_ylabel(ylabel)
    ax[0].grid(True)
    ax[0].legend(ncol=2, fontsize=10)
    ax[0].set_xlim(df.index.values[0] - 1, df.index.values[-1] + 1)
    dy = df[dfcol].max() - df[dfcol].min()
    ax[0].set_ylim(df[dfcol].min() - dy * 0.2, df[dfcol].max() + dy * 0.25)
    box = ax[0].get_position()
    ax[0].set_position([box.x0, box.y0 + 0.02, box.width, box.height * 0.98])

    # Plot 2: CDF
    vals = df[pd.notnull(df[dfcol])][dfcol]
    X2 = np.sort(vals)
    ptile = np.percentile(vals, [0, 5, 50, 95, 100])
    N = len(vals)
    F2 = np.array(range(N)) / float(N) * 100.0
    ax[1].plot(X2, 100.0 - F2)
    ax[1].set_xlabel(f"based on summarized hourly reports, {ylabel}")
    ax[1].set_ylabel("Observed Frequency [%]")
    ax[1].grid(True)
    ax[1].set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    mysort = df.sort_values(by=dfcol, ascending=True)
    info = (
        f"Min: {df[dfcol].min():.2f} {yrfmter(mysort.index[0])}\n"
        f"95th: {ptile[1]:.2f}\n"
        f"Mean: {df[dfcol].mean():.2f}\n"
        f"STD: {df[dfcol].std():.2f}\n"
        f"5th: {ptile[3]:.2f}\n"
        f"Max: {df[dfcol].max():.2f} {yrfmter(mysort.index[-1])}"
    )
    if thisvalue != "M":
        ax[1].axvline(thisvalue, lw=2, color="g")
    ax[1].text(
        0.8,
        0.95,
        info,
        transform=ax[1].transAxes,
        va="top",
        bbox=dict(facecolor="white", edgecolor="k"),
    )
    return fig, df


if __name__ == "__main__":
    plotter({})
