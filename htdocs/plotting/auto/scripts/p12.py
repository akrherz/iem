"""First or Last Date with temp"""
import datetime

from pandas.io.sql import read_sql
import numpy as np
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = dict(
    [
        ("last_high_above", "Last Date At or Above (High Temperature)"),
        ("last_high_below", "Last Date Below (High Temperature)"),
        ("first_high_above", "First Date At or Above (High Temperature)"),
        ("first_high_below", "First Date Below (High Temperature)"),
        ("first_low_above", "First Date At or Above (Low Temperature)"),
        ("first_low_below", "First Date Below (Low Temperature)"),
        ("last_low_above", "Last Date At or Above(Low Temperature)"),
        ("last_low_below", "Last Date Below (Low Temperature)"),
    ]
)
PDICT2 = dict(
    [
        ("calendar", "Compute over Calendar Year"),
        ("winter", "Compute over Winter Season"),
    ]
)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents the yearly first or last date
    of a given high or low temperature along with the number of days that
    year above/below the threshold along with the cumulative distribution
    function for the first date!  When you select a low temperature option,
    the season displayed in the chart and available download spreadsheet
    represents the start year of the winter season.  Rewording, the year 2016
    would represent the period of 1 July 2016 to 30 Jun 2017.
    """
    thisyear = datetime.date.today().year
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="int",
            name="threshold",
            default="90",
            label="Enter Threshold:",
        ),
        dict(
            type="select",
            name="which",
            default="last_high_above",
            label="Date Option:",
            options=PDICT,
        ),
        dict(
            type="select",
            name="season",
            default="calendar",
            label="How to split the year:",
            options=PDICT2,
        ),
        dict(
            type="year",
            name="year",
            default=thisyear,
            max=(thisyear + 1),
            label="Year to Highlight in Chart:",
        ),
    ]
    return desc


def do_labels(ax, extrenum, varname, direction, threshold, season):
    """Helper."""

    ax.set_xlabel(
        ("Date of %s Occurrence%s")
        % (
            extrenum.capitalize(),
            (
                ", Year of December for Winter Season"
                if season == "winter"
                else ""
            ),
        )
    )
    ax.set_ylabel(
        (r"Days with %s %s %s$^\circ$F")
        % (
            varname.capitalize(),
            "At or Above" if direction == "above" else "Below",
            threshold,
        )
    )


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    threshold = ctx["threshold"]
    season = ctx["season"]
    (extrenum, varname, direction) = ctx["which"].split("_")
    year = ctx["year"]

    table = "alldata_%s" % (station[:2],)

    op = "%s %s" % (varname, ">=" if direction == "above" else "<")
    df = read_sql(
        f"""
        with data as (
            SELECT extract(year from day + '%s months'::interval) as season,
            high, low, day from {table} WHERE station = %s
            and day >= '1893-01-01'),
        agg1 as (
            SELECT season - %s as season,
            count(*) as obs,
            min(case when {op} %s then day else null end) as nday,
            max(case when {op} %s then day else null end) as xday,
            sum(case when {op} %s then 1 else 0 end) as count
            from data GROUP by season)
    SELECT season::int, count, obs, nday, extract(doy from nday) as nday_doy,
    xday, extract(doy from xday) as xday_doy from agg1
    ORDER by season ASC
    """,
        pgconn,
        params=(
            6 if season == "winter" else 0,
            station,
            1 if season == "winter" else 0,
            threshold,
            threshold,
            threshold,
        ),
        index_col="season",
    )
    # We need to do some magic to julian dates straight
    if season == "winter":
        # drop the first row
        df = df.drop(df.index.values[0])
        df.loc[df["nday_doy"] < 183, "nday_doy"] += 365.0
        df.loc[df["xday_doy"] < 183, "xday_doy"] += 365.0
    # Set NaN where we did not meet conditions
    zeros = df[df["count"] == 0].index.values
    col = "xday_doy" if extrenum == "last" else "nday_doy"
    df2 = df[df["count"] > 0]
    if df2.empty:
        raise NoDataFound("No data found.")
    title = ("%s [%s] %s Date and Days\n" r"%s %s$^\circ$F") % (
        ctx["_nt"].sts[station]["name"],
        station,
        extrenum.capitalize(),
        PDICT["%s_%s_%s" % (extrenum, varname, direction)],
        threshold,
    )
    (fig, ax) = figure_axes(title=title)
    # The present year value may be so low that it destorts the plot
    lastval = df2.iloc[-1]["count"]
    minval = df2[df2["count"] > lastval]["count"].min()
    pltdf = df2
    if lastval < 10 and (minval - lastval) > 30:
        pltdf = df2[df2["count"] > lastval]
    ax.scatter(pltdf[col], pltdf["count"])
    ax.grid(True)
    do_labels(ax, extrenum, varname, direction, threshold, season)

    xticks = []
    xticklabels = []
    for i in np.arange(df2[col].min() - 5, df2[col].max() + 5, 1):
        ts = datetime.datetime(2000, 1, 1) + datetime.timedelta(days=i)
        if ts.day == 1:
            xticks.append(i)
            xticklabels.append(ts.strftime("%-d %b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)

    ax2 = ax.twinx()
    sortvals = np.sort(df2[col].values)
    yvals = np.arange(len(sortvals)) / float(len(sortvals))
    ax2.plot(sortvals, yvals * 100.0, color="r")
    ax2.set_ylabel("Accumulated Frequency [%] (red line)", color="r")
    ax2.set_yticks([0, 25, 50, 75, 100])

    avgd = datetime.datetime(2000, 1, 1) + datetime.timedelta(
        days=int(df2[col].mean())
    )
    ax.text(
        0.01,
        0.99,
        (
            "%s year(s) failed threshold %s\nAvg Date: %s\n"
            "Avg Count: %.1f days"
        )
        % (
            len(zeros),
            ("[" + ",".join([str(z) for z in zeros]) + "]")
            if len(zeros) < 4
            else "",
            avgd.strftime("%-d %b"),
            df2["count"].mean(),
        ),
        transform=ax.transAxes,
        va="top",
        bbox=dict(color="white"),
    )

    ax.set_xlim(df2[col].min() - 10, df2[col].max() + 10)
    ax2.set_ylim(0, 100)

    idx = df2[col].idxmax()
    if idx != year:
        ax.text(
            df2.at[idx, col] + 1,
            df2.at[idx, "count"],
            "%s" % (idx,),
            ha="left",
        )
    idx = df2[col].idxmin()
    if idx != year:
        ax.text(
            df2.at[idx, col] - 1,
            df2.at[idx, "count"],
            "%s" % (idx,),
            va="bottom",
        )
    idx = df2["count"].idxmax()
    if idx != year:
        ax.text(
            df2.at[idx, col] + 1,
            df2.at[idx, "count"],
            f"{idx}",
            va="bottom",
        )
    if year in df2.index:
        df3 = df2.loc[year]
        if df3["count"] >= minval:
            ax.scatter(df3[col], df3["count"], zorder=5, color="r")
            ax.text(df3[col], df3["count"] + 1, f"{year}", zorder=5, color="r")
            ax.axhline(df3["count"])
        else:
            fig.text(
                0.04,
                0.05,
                f"{year} value of {df3['count']} day(s) not shown",
            )
        ax.axvline(df3[col])
        ax.annotate(
            str(year),
            (df3[col], 0.99),
            xycoords=("data", "axes fraction"),
            color="b",
            rotation=90,
            va="top",
        )
    return fig, df


if __name__ == "__main__":
    plotter(
        dict(
            which="first_high_above",
            threshold=70,
            year=2021,
        )
    )
