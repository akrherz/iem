"""Daily departures"""
import datetime

from pandas.io.sql import read_sql
import matplotlib.dates as mdates
import matplotlib.colors as mpcolors
from pyiem.plot import get_cmap
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = dict(
    (
        ("avg", "Daily Average Temperature"),
        ("gdd", "Growing Degree Days"),
        ("high", "High Temperature"),
        ("low", "Low Temperature"),
    )
)
OPTDICT = dict(
    (
        ("diff", "Difference in Degrees F"),
        ("sigma", "Difference in Standard Deviations"),
        ("ptile", "Percentile"),
    )
)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents the daily high, low, or
    average temperature departure.  The average temperature is simply the
    average of the daily high and low.  The daily climatology is simply based
    on the period of record observations for the site."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
            label="Select Station:",
            network="IACLIMATE",
        ),
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
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    year = ctx["year"]
    varname = ctx["var"]
    how = ctx["how"]
    gddbase = ctx["gddbase"]
    gddceil = ctx["gddceil"]

    table = f"alldata_{station[:2]}"

    df = read_sql(
        f"""
    WITH data as (
     select day, year, sday,
     high,
     low,
     (high+low)/2. as temp,
     gddxx(%s, %s, high, low) as gdd,
     rank() OVER (PARTITION by sday ORDER by high ASC) as high_ptile,
     rank() OVER (PARTITION by sday ORDER by (high+low)/2. ASC) as temp_ptile,
     rank() OVER (PARTITION by sday ORDER by low ASC) as low_ptile,
     rank() OVER (PARTITION by sday
        ORDER by gddxx(%s, %s, high, low) ASC) as gdd_ptile
     from {table} where station = %s
    ), climo as (
     SELECT sday, avg(high) as avg_high, avg(low) as avg_low,
     avg((high+low)/2.) as avg_temp, stddev(high) as stddev_high,
     stddev(low) as stddev_low, stddev((high+low)/2.) as stddev_temp,
     avg(gddxx(%s, %s, high, low)) as avg_gdd,
     stddev(gddxx(%s, %s, high, low)) as stddev_gdd,
     count(*)::float as years
     from {table} WHERE station = %s GROUP by sday
    )
    SELECT day,
    d.high - c.avg_high as high_diff,
    (d.high - c.avg_high) / c.stddev_high as high_sigma,
    d.low - c.avg_low as low_diff,
    (d.low - c.avg_low) / c.stddev_low as low_sigma,
    d.temp - c.avg_temp as avg_diff,
    (d.temp - c.avg_temp) / c.stddev_temp as avg_sigma,
    d.gdd - c.avg_gdd as gdd_diff,
    (d.gdd - c.avg_gdd) / greatest(c.stddev_gdd, 0.1) as gdd_sigma,
    d.high,
    c.avg_high,
    d.low,
    c.avg_low,
    d.temp,
    c.avg_temp,
    d.gdd,
    c.avg_gdd,
    high_ptile / years * 100. as high_ptile,
    low_ptile / years * 100. as low_ptile,
    temp_ptile / years * 100. as temp_ptile,
    gdd_ptile / years * 100. as gdd_ptile
    from data d JOIN climo c on
    (c.sday = d.sday) WHERE d.year = %s ORDER by day ASC
    """,
        pgconn,
        params=(
            gddbase,
            gddceil,
            gddbase,
            gddceil,
            station,
            gddbase,
            gddceil,
            gddbase,
            gddceil,
            station,
            year,
        ),
        index_col=None,
    )

    (fig, ax) = figure_axes(apctx=ctx)
    diff = df[varname + "_" + how].values
    if how == "ptile" and "cmap" in ctx:
        bins = range(0, 101, 10)
        cmap = get_cmap(ctx["cmap"])
        norm = mpcolors.BoundaryNorm(bins, cmap.N)
        colors = cmap(norm(diff))
        ax.bar(df["day"].values, diff, color=colors, align="center")
        ax.set_yticks(bins)
    else:
        bars = ax.bar(df["day"].values, diff, fc="b", ec="b", align="center")
        for i, _bar in enumerate(bars):
            if diff[i] > 0:
                _bar.set_facecolor("r")
                _bar.set_edgecolor("r")
    ax.grid(True)
    if how == "diff":
        ax.set_ylabel(r"%s Departure $^\circ$F" % (PDICT[varname],))
    elif how == "ptile":
        ax.set_ylabel("%s Percentile (100 highest)" % (PDICT[varname],))
    else:
        ax.set_ylabel(r"%s Std Dev Departure ($\sigma$)" % (PDICT[varname],))
    if varname == "gdd":
        ax.set_xlabel(
            "Growing Degree Day Base: %s Ceiling: %s" % (gddbase, gddceil)
        )
    ax.set_title(
        ("%s %s\nYear %s Daily %s %s")
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            year,
            PDICT[varname],
            "Departure" if how != "ptile" else "Percentile",
        )
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.set_major_locator(mdates.DayLocator(1))

    return fig, df


if __name__ == "__main__":
    plotter({})
