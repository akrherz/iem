"""
Based on hourly or better METAR reports, this
plot displays the longest periods above or below a given temperature
threshold.  There are plenty of caveats to this plot, including missing
data periods and data during the 1960s that only has
reports every three hours. This
plot also stops any computed streak when it encounters a data gap greater
than three hours.

<p>You can additionally set a secondary threshold which then makes this
autoplot compute streaks within a range of values.</p>

<p><strong>Updated 16 Jan 2024:</strong> The option to control the minimum
number of hours was removed.  This option did not add much value as folks
generally wish to see the top 10 longest streaks.</p>
"""

import datetime
import operator
from zoneinfo import ZoneInfo

import pandas as pd
from pyiem.database import get_dbconnc
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context

PDICT = {
    "above": "At or Above Threshold...",
    "below": "Below Threshold...",
    "aob": "At or Below Threshold...",
}
PDICT2 = {
    "tmpf": "Air Temperature",
    "feel": "Feels Like Temperature",
    "dwpf": "Dew Point Temperature",
    "mslp": "Sea Level Pressure",
    "vsby": "Visibility",
}
MDICT = {
    "all": "Calendar Year",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "octmar": "October thru March",
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
    ]
    return desc


def plot(ax, xbase, valid, tmpf, lines: list) -> bool:
    """Our plotting function"""
    if len(valid) < 2:
        return True
    interval = datetime.timedelta(hours=1)
    # lines are sorted from shortest to longest, so the first one is the
    # minimum length when we are full
    if len(lines) == 10:
        interval = lines[0].interval

    thisinterval = valid[-1] - valid[0]
    if thisinterval < interval:
        return True
    # Figure out the position that this line should be inserted into
    pos = None
    for i, line in enumerate(lines):
        if thisinterval < line.interval:
            pos = i
            break
    if pos is None:
        pos = len(lines)

    delta = (valid[-1] - valid[0]).total_seconds()
    mylbl = (
        f"{valid[0].year}\n{int(delta / 86400):.0f}d"
        f"{((delta % 86400) / 3600.0):.0f}h"
    )
    seconds = [(v - xbase).total_seconds() for v in valid]
    line = ax.plot(seconds, tmpf, lw=2, label=mylbl.replace("\n", " "))[0]
    line.hours = round((valid[-1] - valid[0]).seconds / 3600.0, 2)
    line.days = (valid[-1] - valid[0]).days
    line.mylbl = mylbl
    line.period_start = valid[0]
    line.period_end = valid[-1]
    line.interval = thisinterval
    line.labelx = seconds[tmpf.index(min(tmpf))]
    line.labely = min(tmpf)
    lines.insert(pos, line)
    if len(lines) > 10:
        lines.pop(0).remove()
    return True


def plot_text(ax, lines):
    """Add text to ax"""
    for line in lines:
        ax.text(
            line.labelx,
            line.labely,
            line.mylbl,
            ha="center",
            va="center",
            bbox={"color": line.get_color()},
            color="white",
        )


def compute_xlabels(ax, xbase):
    """Figure out how to make pretty xaxis labels"""
    # values are in seconds
    xlim = ax.get_xlim()
    x0 = xbase + datetime.timedelta(seconds=xlim[0])
    x0 = x0.replace(hour=0, minute=0)
    x1 = xbase + datetime.timedelta(seconds=xlim[1])
    x1 = x1.replace(hour=0, minute=0) + datetime.timedelta(days=1)
    xticks = []
    xticklabels = []
    # Pick a number of days so that we end up with 8 labels
    delta = int((xlim[1] - xlim[0]) / 86400.0 / 7)
    if delta == 0:
        delta = 1
    for x in range(
        int((x0 - xbase).total_seconds()),
        int((x1 - xbase).total_seconds()),
        86400 * delta,
    ):
        xticks.append(x)
        ts = xbase + datetime.timedelta(seconds=x)
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
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "octmar":
        months = [10, 11, 12, 1, 2, 3]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        months = [ts.month]

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    tzname = ctx["_nt"].sts[station]["tzname"]
    tzinfo = ZoneInfo(tzname)
    rnd = 0 if varname not in ["mslp", "vsby"] else 2
    cursor.execute(
        f"""
        SELECT valid at time zone 'UTC' as utc_valid,
        round({varname}::numeric,{rnd}) as d
        from alldata where station = %s {year_limiter}
        and {varname} is not null and
        extract(month from valid at time zone %s) = ANY(%s)
        ORDER by valid ASC
        """,
        (station, tzname, months),
    )
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

    valids = []
    tmpf = []
    lines = []
    # Figure out bounds check values
    lower = threshold
    upper = 9999
    if ctx.get("t2") is None:
        if mydir in ["below", "aob"]:
            lower = -9999
            upper = threshold
        label = f"{mydir} {threshold}"
    else:
        upper = ctx["t2"]
        if mydir in ["below", "aob"]:
            lower, upper = upper, lower
        label = (
            f"within range {lower} <= x"
            f" {'<' if mydir == 'below' else '<='} {upper}"
        )
    subtitle = (
        f"{MDICT.get(month)} :: Streaks {PDICT2[varname]} {label} {units}"
    )
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    ax = fig.add_axes([0.07, 0.25, 0.6, 0.65])

    threshold = datetime.timedelta(hours=3)
    reset_valid = datetime.datetime(1910, 1, 1, tzinfo=tzinfo)
    xbase = reset_valid

    op2 = operator.lt if mydir == "below" else operator.le
    for row in cursor:
        valid = row["utc_valid"].replace(tzinfo=datetime.timezone.utc)
        ireset = False
        # This is tricky, we need to resolve when time resets.
        if valid > reset_valid:
            _tmp = (
                datetime.datetime(valid.year, months[-1], 1)
                + datetime.timedelta(days=32)
            ).replace(day=1)
            if month in ["winter", "octmar"]:
                _tmp = _tmp.replace(year=valid.year + 1)
            reset_valid = datetime.datetime(
                _tmp.year, _tmp.month, 1, tzinfo=tzinfo
            )
            xbase = datetime.datetime(
                _tmp.year - 1, _tmp.month, 1, tzinfo=tzinfo
            )
            ireset = True
        if ireset or (valids and ((valid - valids[-1]) > threshold)):
            if not plot(ax, xbase, valids, tmpf, lines):
                break
            valids = []
            tmpf = []
        if operator.ge(row["d"], lower) and op2(row["d"], upper):
            valids.append(valid)
            tmpf.append(row["d"])
        else:
            valids.append(valid)
            tmpf.append(row["d"])
            if not plot(ax, xbase, valids, tmpf, lines):
                break
            valids = []
            tmpf = []
    pgconn.close()

    plot(ax, xbase, valids, tmpf, lines)
    compute_xlabels(ax, xbase)
    rows = []
    for line in lines:
        # Ensure we don't send datetimes to pandas
        rows.append(
            dict(
                start_utc=line.period_start.strftime("%Y-%m-%d %H:%M+00"),
                end_utc=line.period_end.strftime("%Y-%m-%d %H:%M+00"),
                hours=line.hours,
                days=line.days,
            )
        )
    df = pd.DataFrame(rows)

    ax.grid(True)
    ax.set_ylabel(f"{PDICT2.get(varname)} {units}")
    ax.set_xlabel(
        "* Due to timezones and leapday, there is some ambiguity"
        " with the plotted dates"
    )
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.7, -0.165),
        fancybox=True,
        shadow=True,
        ncol=5,
        fontsize=12,
        columnspacing=1,
    )
    plot_text(ax, lines)
    label = "Start                     End   Hours\n"
    for line in lines:
        sts = line.period_start.astimezone(tzinfo)
        ets = line.period_end.astimezone(tzinfo)
        label += (
            f" {sts.strftime('%m/%d/%y %I:%M %p')} "
            f"{ets.strftime('%m/%d/%y %I:%M %p')} "
            f"{line.interval.total_seconds() / 3600.:4.0f}\n"
        )
    label += tzname
    fig.text(0.99, 0.9, label, ha="right", va="top", fontsize=10)
    return fig, df


if __name__ == "__main__":
    plotter({})
