"""monthly comparisons"""
import datetime
import calendar

import numpy as np
from scipy import stats
from pandas.io.sql import read_sql
import pandas as pd
from pyiem.plot import figure_axes
from pyiem import network, util
from pyiem.exceptions import NoDataFound

PDICT = dict(
    (
        ("total_precip", "Total Precipitation"),
        ("avg_temp", "Average Temperature"),
        ("max_high", "Maximum High Temperature"),
        ("avg_high", "Average High Temperature"),
        ("min_high", "Minimum High Temperature"),
        ("max_low", "Maximum Low Temperature"),
        ("avg_low", "Average Low Temperature"),
        ("min_low", "Minimum Low Temperature"),
        ("days_high_aoa", "Days with High At or Above"),
        ("cdd65", "Cooling Degree Days (base 65)"),
        ("hdd65", "Heating Degree Days (base 65)"),
        ("gdd32", "Growing Degree Days (base 32)"),
        ("gdd41", "Growing Degree Days (base 41)"),
        ("gdd46", "Growing Degree Days (base 46)"),
        ("gdd48", "Growing Degree Days (base 48)"),
        ("gdd50", "Growing Degree Days (base 50)"),
        ("gdd51", "Growing Degree Days (base 51)"),
        ("gdd52", "Growing Degree Days (base 52)"),
    )
)

UNITS = {
    "total_precip": "inch",
    "avg_temp": "F",
    "max_high": "F",
    "avg_high": "F",
    "min_high": "F",
    "max_low": "F",
    "avg_low": "F",
    "min_low": "F",
    "days_high_aoa": "days",
    "cdd65": "F",
    "hdd65": "F",
    "gdd32": "F",
    "gdd41": "F",
    "gdd46": "F",
    "gdd48": "F",
    "gdd50": "F",
    "gdd51": "F",
    "gdd52": "F",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=60)
    desc[
        "description"
    ] = """This app allows the arbitrary comparison of months
    against other months.  When the period of months wraps around a new
    year, the app attempts to keep this situation straight with Dec and Jan
    following each other.  The periods are combined together based on the
    year of the beginning month of each period. If there is a metric you
    wished to see added to this analysis, please
    <a href="/info/contacts.php">let us know</a>!"""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0000",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(
            type="int",
            name="threshold",
            default="93",
            label="Daily Temperature Threshold (when appropriate)",
        ),
        dict(
            type="month",
            name="month1",
            default=yesterday.month,
            label="Month 1 for Comparison",
        ),
        dict(
            type="int",
            name="num1",
            default=2,
            label="Number of Additional Months for Comparison 1",
        ),
        dict(
            type="select",
            options=PDICT,
            default="total_precip",
            name="var1",
            label="Comparison 1 Variable",
        ),
        dict(
            type="month",
            name="month2",
            default=yesterday.month,
            label="Month 2 for Comparison",
        ),
        dict(
            type="int",
            name="num2",
            default=2,
            label="Number of Additional Months for Comparison 2",
        ),
        dict(
            type="select",
            options=PDICT,
            default="avg_temp",
            name="var2",
            label="Comparison 2 Variable",
        ),
    ]
    return desc


def compute_months_and_offsets(start, count):
    """Figure out an array of values"""
    months = [start]
    offsets = [0]
    for i in range(1, count):
        nextval = start + i
        if nextval > 12:
            nextval -= 12
            offsets.append(1)
        else:
            offsets.append(0)
        months.append(nextval)

    return months, offsets


def combine(df, months, offsets):
    """combine"""
    # To allow for periods that cross years! We create a second dataframe with
    # the year shifted back one!
    df_shift = df.copy()
    df_shift.index = df_shift.index - 1

    # We create the xaxis dataset
    xdf = df[df["month"] == months[0]].copy()
    for i, month in enumerate(months):
        if i == 0:
            continue
        if offsets[i] == 1:
            thisdf = df_shift[df_shift["month"] == month]
        else:
            thisdf = df[df["month"] == month]
        # Do our combinations, we divide out later when necessary
        for v in PDICT:
            xdf[v] = xdf[v] + thisdf[v]
        tmpdf = pd.DataFrame({"a": xdf["max_high"], "b": thisdf["max_high"]})
        xdf["max_high"] = tmpdf.max(axis=1)
    if len(months) > 1:
        xdf["avg_temp"] = xdf["avg_temp"] / float(len(months))

    return xdf


def plotter(fdict):
    """Go"""
    pgconn = util.get_dbconn("coop")

    today = datetime.date.today()
    ctx = util.get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    threshold = ctx["threshold"]
    month1 = ctx["month1"]
    varname1 = ctx["var1"]
    num1 = min([12, ctx["num1"]])
    month2 = ctx["month2"]
    varname2 = ctx["var2"]
    num2 = min([12, ctx["num2"]])
    months1, offsets1 = compute_months_and_offsets(month1, num1)
    months2, offsets2 = compute_months_and_offsets(month2, num2)
    nt = network.Table(f"{station[:2]}CLIMATE")
    # Compute the monthly totals
    df = read_sql(
        f"""
    SELECT year, month, avg((high+low)/2.) as avg_temp,
    avg(high) as avg_high, min(high) as min_high,
    avg(low) as avg_low, max(low) as max_low,
    sum(precip) as total_precip, max(high) as max_high, min(low) as min_low,
    sum(case when high >= %s then 1 else 0 end) as days_high_aoa,
    sum(cdd(high, low, 65)) as cdd65,
    sum(hdd(high, low, 65)) as hdd65,
    sum(gddxx(32, 86, high, low)) as gdd32,
    sum(gddxx(41, 86, high, low)) as gdd41,
    sum(gddxx(46, 86, high, low)) as gdd46,
    sum(gddxx(48, 86, high, low)) as gdd48,
    sum(gddxx(50, 86, high, low)) as gdd50,
    sum(gddxx(51, 86, high, low)) as gdd51,
    sum(gddxx(52, 86, high, low)) as gdd52
    from alldata_{station[:2]}
    WHERE station = %s and day < %s GROUP by year, month
    """,
        pgconn,
        params=(threshold, station, today.replace(day=1)),
        index_col="year",
    )

    xdf = combine(df, months1, offsets1)
    ydf = combine(df, months2, offsets2)
    if xdf.empty or ydf.empty:
        raise NoDataFound("Sorry, could not find data.")

    resdf = pd.DataFrame(
        {
            "%s_1" % (varname1,): xdf[varname1],
            "%s_2" % (varname2,): ydf[varname2],
        }
    )
    resdf = resdf.dropna()
    title = (
        "%s-%s %s [%s]\n"
        "Comparison of Monthly Periods, Quadrant Frequency Labelled"
    ) % (
        resdf.index.min(),
        resdf.index.max(),
        nt.sts[station]["name"],
        station,
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.scatter(
        resdf[varname1 + "_1"],
        resdf[varname2 + "_2"],
        marker="s",
        facecolor="b",
        edgecolor="b",
        label=None,
        zorder=3,
    )
    ax.grid(True)

    h_slope, intercept, r_value, _, _ = stats.linregress(
        resdf[varname1 + "_1"], resdf[varname2 + "_2"]
    )
    y = (
        h_slope
        * np.arange(resdf[varname1 + "_1"].min(), resdf[varname1 + "_1"].max())
        + intercept
    )
    ax.plot(
        np.arange(resdf[varname1 + "_1"].min(), resdf[varname1 + "_1"].max()),
        y,
        lw=2,
        color="r",
        label="Slope=%.2f R$^2$=%.2f" % (h_slope, r_value ** 2),
    )
    ax.legend(fontsize=10)
    xmonths = ", ".join([calendar.month_abbr[x] for x in months1])
    ymonths = ", ".join([calendar.month_abbr[x] for x in months2])
    t1 = "" if varname1 not in ["days_high_aoa"] else " %.0f" % (threshold,)
    t2 = "" if varname2 not in ["days_high_aoa"] else " %.0f" % (threshold,)
    x = resdf["%s_1" % (varname1,)].mean()
    y = resdf["%s_2" % (varname2,)].mean()
    ax.set_xlabel(
        "%s\n%s%s [%s], Avg: %.1f"
        % (xmonths, PDICT[varname1], t1, UNITS[varname1], x),
        fontsize=12,
    )
    ax.set_ylabel(
        "%s\n%s%s [%s], Avg: %.1f"
        % (ymonths, PDICT[varname2], t2, UNITS[varname2], y),
        fontsize=12,
    )

    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.05, box.width, box.height * 0.95]
    )
    ax.axhline(y, linestyle="--", color="g")
    ax.axvline(x, linestyle="--", color="g")
    ur = len(
        resdf[
            (resdf["%s_1" % (varname1,)] >= x)
            & (resdf["%s_2" % (varname2,)] >= y)
        ].index
    )
    ax.text(
        0.95,
        0.75,
        "%s (%.1f%%)" % (ur, ur / float(len(resdf.index)) * 100.0),
        color="tan",
        fontsize=24,
        transform=ax.transAxes,
        ha="right",
        zorder=2,
    )
    lr = len(
        resdf[
            (resdf["%s_1" % (varname1,)] >= x)
            & (resdf["%s_2" % (varname2,)] < y)
        ].index
    )
    ax.text(
        0.95,
        0.25,
        "%s (%.1f%%)" % (lr, lr / float(len(resdf.index)) * 100.0),
        color="tan",
        fontsize=24,
        transform=ax.transAxes,
        ha="right",
        zorder=2,
    )
    ll = len(
        resdf[
            (resdf["%s_1" % (varname1,)] < x)
            & (resdf["%s_2" % (varname2,)] < y)
        ].index
    )
    ax.text(
        0.05,
        0.25,
        "%s (%.1f%%)" % (ll, ll / float(len(resdf.index)) * 100.0),
        color="tan",
        fontsize=24,
        transform=ax.transAxes,
        ha="left",
        zorder=2,
    )
    ul = len(
        resdf[
            (resdf["%s_1" % (varname1,)] < x)
            & (resdf["%s_2" % (varname2,)] >= y)
        ].index
    )
    ax.text(
        0.05,
        0.75,
        "%s (%.1f%%)" % (ul, ul / float(len(resdf.index)) * 100.0),
        color="tan",
        fontsize=24,
        transform=ax.transAxes,
        ha="left",
        zorder=2,
    )
    return fig, resdf


if __name__ == "__main__":
    plotter({})
