"""
Based on hourly or better METAR reports, this
plot displays the longest periods above or below a given temperature
threshold.  There are plenty of caveats to this plot, including missing
data periods and data during the 1960s that only has
reports every three hours.  This plot also limits the number of lines
drawn to 10, so if you hit the limit, please change the thresholds.  This
plot also stops any computed streak when it encounters a data gap greater
than three hours.

<p>You can additionally set a secondary threshold which then makes this
autoplot compute streaks within a range of values.</p>
"""
import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconnc

PDICT = {"above": "At or Above Threshold...", "below": "Below Threshold..."}
PDICT2 = {
    "tmpf": "Air Temperature",
    "feel": "Feels Like Temperature",
    "dwpf": "Dew Point Temperature",
    "mslp": "Sea Level Pressure",
    "vsby": "Visibility",
}
MDICT = {
    "all": "Entire Year",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    # no worky ('winter', 'Winter (DJF)'),
    "summer": "Summer (JJA)",
    # no worky ('octmar', 'October thru March'),
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 86400, "data": True}
    year_range = f"1928-{datetime.date.today().year}"
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="m",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="text",
            name="yrange",
            default=year_range,
            optional=True,
            label="Inclusive Range of Years to Include (optional)",
        ),
        dict(
            type="select",
            name="dir",
            default="above",
            label="Threshold Direction:",
            options=PDICT,
        ),
        dict(
            type="select",
            name="var",
            default="tmpf",
            label="Which variable",
            options=PDICT2,
        ),
        dict(
            type="float",
            name="threshold",
            default=50,
            label="Temperature (F) / Pressure (mb) / Vis (mi) Threshold:",
        ),
        dict(
            optional=True,
            type="float",
            name="t2",
            default=60,
            label=(
                "Secondary Temperature (F) / Pressure (mb) / Vis (mi) "
                "Threshold (for range queries)"
            ),
        ),
        dict(
            type="int",
            name="hours",
            default=36,
            label="Minimum Period to Plot (Hours):",
        ),
    ]
    return desc


def plot(ax, interval, valid, tmpf, lines, mydir, month):
    """Our plotting function"""
    if len(lines) > 10 or len(valid) < 2 or (valid[-1] - valid[0]) < interval:
        return lines
    if len(lines) == 10:
        ax.text(
            0.5,
            0.9,
            "ERROR: Limit of 10 lines reached",
            transform=ax.transAxes,
        )
        return lines
    delta = (valid[-1] - valid[0]).total_seconds()
    i = tmpf.index(min(tmpf))
    mylbl = (
        f"{valid[0].year}\n{int(delta / 86400):.0f}d"
        f"{((delta % 86400) / 3600.0):.0f}h"
    )
    x0 = valid[0].replace(month=1, day=1, hour=0, minute=0)
    offset = 0
    if mydir == "below" and valid[0].month < 7 and month == "all":
        offset = 366.0 * 86400.0
    seconds = [((v - x0).total_seconds() + offset) for v in valid]
    lines.append(
        ax.plot(seconds, tmpf, lw=2, label=mylbl.replace("\n", " "))[0]
    )
    lines[-1].hours = round((valid[-1] - valid[0]).seconds / 3600.0, 2)
    lines[-1].days = (valid[-1] - valid[0]).days
    lines[-1].mylbl = mylbl
    lines[-1].period_start = valid[0]
    lines[-1].period_end = valid[-1]
    ax.text(
        seconds[i],
        tmpf[i],
        mylbl,
        ha="center",
        va="center",
        bbox=dict(color=lines[-1].get_color()),
        color="white",
    )
    return lines


def compute_xlabels(ax):
    """Figure out how to make pretty xaxis labels"""
    # values are in seconds
    xlim = ax.get_xlim()
    x0 = datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds=xlim[0])
    x0 = x0.replace(hour=0, minute=0)
    x1 = datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds=xlim[1])
    x1 = x1.replace(hour=0, minute=0) + datetime.timedelta(days=1)
    xticks = []
    xticklabels = []
    # Pick a number of days so that we end up with 8 labels
    delta = int((xlim[1] - xlim[0]) / 86400.0 / 7)
    if delta == 0:
        delta = 1
    for x in range(
        int((x0 - datetime.datetime(2000, 1, 1)).total_seconds()),
        int((x1 - datetime.datetime(2000, 1, 1)).total_seconds()),
        86400 * delta,
    ):
        xticks.append(x)
        ts = datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds=x)
        xticklabels.append(ts.strftime("%-d\n%b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)


def plotter(fdict):
    """Go"""
    pgconn, cursor = get_dbconnc("asos")

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    threshold = ctx["threshold"]
    mydir = ctx["dir"]
    hours = ctx["hours"]
    varname = ctx["var"]
    month = ctx["m"] if fdict.get("month") is None else fdict.get("month")

    year_limiter = ""
    y1, y2 = None, None
    if "yrange" in ctx:
        y1, y2 = ctx["yrange"].split("-")
        year_limiter = (
            f" and valid >= '{int(y1)}-01-01' and "
            f"valid < '{int(y2) + 1}-01-01' "
        )
    if month == "all":
        months = list(range(1, 13))
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    rnd = 0 if varname not in ["mslp", "vsby"] else 2
    cursor.execute(
        f"""
        SELECT valid, round({varname}::numeric,{rnd}) as d
        from alldata where station = %s {year_limiter}
        and {varname} is not null and extract(month from valid) = ANY(%s)
        ORDER by valid ASC
        """,
        (station, months),
    )
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    units = r"$^\circ$F"
    if varname == "mslp":
        units = "mb"
    elif varname == "vsby":
        units = "mile"
    title = (
        f"{y1 if y1 is not None else ab.year}-"
        f"{y2 if y2 is not None else datetime.datetime.now().year} "
        f"{ctx['_sname']}"
    )
    interval = datetime.timedelta(hours=hours)

    valid = []
    tmpf = []
    year = 0
    lines = []
    # Figure out bounds check values
    lower = threshold
    upper = 9999
    if ctx.get("t2") is None:
        if mydir == "below":
            lower = -9999
            upper = threshold
        label = f"{mydir} {threshold}"
    else:
        upper = ctx["t2"]
        if mydir == "below":
            lower, upper = upper, lower
        label = f"within range {lower} <= x < {upper}"
    subtitle = (
        f"{MDICT.get(month)} :: {int(hours / 24)}d{(hours % 24):.0f}h+ "
        f"Streaks {label} {units}"
    )
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)

    for row in cursor:
        if (month != "all" and year != row["valid"].year) or (
            valid and (row["valid"] - valid[-1]) > datetime.timedelta(hours=3)
        ):
            year = row["valid"].year
            lines = plot(ax, interval, valid, tmpf, lines, mydir, month)
            valid = []
            tmpf = []
        if lower <= row["d"] < upper:
            valid.append(row["valid"])
            tmpf.append(row["d"])
        else:
            valid.append(row["valid"])
            tmpf.append(row["d"])
            lines = plot(ax, interval, valid, tmpf, lines, mydir, month)
            valid = []
            tmpf = []
    pgconn.close()

    lines = plot(ax, interval, valid, tmpf, lines, mydir, month)
    compute_xlabels(ax)
    rows = []
    for line in lines:
        # Ensure we don't send datetimes to pandas
        rows.append(
            dict(
                start=line.period_start.strftime("%Y-%m-%d %H:%M"),
                end=line.period_end.strftime("%Y-%m-%d %H:%M"),
                hours=line.hours,
                days=line.days,
            )
        )
    df = pd.DataFrame(rows)

    ax.grid(True)
    ax.set_ylabel(f"{PDICT2.get(varname)} {units}")
    # ax.axhline(32, linestyle='-.', linewidth=2, color='k')
    # ax.set_ylim(bottom=43)
    ax.set_xlabel(
        "* Due to timezones and leapday, there is some ambiguity"
        " with the plotted dates"
    )
    ax.set_position([0.1, 0.25, 0.85, 0.65])
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.165),
        fancybox=True,
        shadow=True,
        ncol=5,
        fontsize=12,
        columnspacing=1,
    )
    return fig, df


if __name__ == "__main__":
    plotter({})
