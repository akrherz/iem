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

import operator
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd
from matplotlib.axes import Axes
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from sqlalchemy.engine import Connection

from iemweb.util import month2months

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
    year_range = f"1900-{date.today().year}"
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
            oldname="month",
        ),
        dict(
            type="text",
            name="yrange",
            default=year_range,
            optional=True,
            label="Inclusive Range of Years to Include (optional)",
            pattern=r"^\d{4}\s*-\s*\d{4}$",
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


def plot(ax, xbase, valid: list, tmpf, lines: list, tzinfo) -> bool:
    """Our plotting function"""
    if len(valid) < 2:
        return True
    interval = timedelta(hours=1)
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
        f"{valid[0].year} "
        f"{int(delta / 86400):.0f}d{((delta % 86400) / 3600.0):.0f}h "
        f"({delta / 3600.0:.1f} hrs)\n"
        f"{valid[0].astimezone(tzinfo).strftime('%Y-%m-%d %I:%M %p')} "
        f"{valid[-1].astimezone(tzinfo).strftime('%Y-%m-%d %I:%M %p')}"
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


def plot_text(ax: Axes, lines: list):
    """Add text to ax"""
    ypos = 0.92
    interval = None
    for line in lines[::-1]:
        if interval is None:
            rank = 1
        elif line.interval < interval:
            rank += 1
        interval = line.interval
        ax.annotate(
            f"#{rank}. {line.mylbl}",
            xy=(line.labelx, line.labely),
            xytext=(1.03, ypos),  # Point to SW corner
            textcoords="axes fraction",
            ha="left",
            va="bottom",
            bbox={"color": line.get_color()},
            color="white",
            arrowprops=dict(
                arrowstyle="->",
                relpos=(0, 0),
                color=line.get_color(),
            ),
            annotation_clip=False,
        )
        ypos -= 0.1


def compute_xlabels(ax, xbase):
    """Figure out how to make pretty xaxis labels"""
    # values are in seconds
    xlim = ax.get_xlim()
    x0 = xbase + timedelta(seconds=xlim[0])
    x0 = x0.replace(hour=0, minute=0)
    x1 = xbase + timedelta(seconds=xlim[1])
    x1 = x1.replace(hour=0, minute=0) + timedelta(days=1)
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
        ts = xbase + timedelta(seconds=x)
        xticklabels.append(ts.strftime("%-d\n%b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)


@with_sqlalchemy_conn("asos")
def plotter(ctx: dict, conn: Connection | None = None):
    """Go"""
    station = ctx["zstation"]
    threshold = ctx["threshold"]
    mydir = ctx["dir"]
    varname = ctx["var"]
    month = ctx["m"]

    months = month2months(month)

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    tzname = ctx["_nt"].sts[station]["tzname"]
    tzinfo = ZoneInfo(tzname)
    params = {
        "rnd": 0 if varname not in ["mslp", "vsby"] else 2,
        "station": station,
        "tzname": tzname,
        "months": months,
    }
    year_limiter = ""
    y1, y2 = None, None
    if "yrange" in ctx:
        y1, y2 = ctx["yrange"].split("-")
        year_limiter = " and valid >= :yr1 and valid < :yr2 "
        params["yr1"] = date(int(y1), 1, 1)
        params["yr2"] = date(int(y2) + 1, 1, 1)
    res = conn.execute(
        sql_helper(
            """
        SELECT valid at time zone 'UTC' as utc_valid,
        round({varname}::numeric, :rnd) as d
        from alldata where station = :station {year_limiter}
        and {varname} is not null and
        extract(month from valid at time zone :tzname) = ANY(:months)
        ORDER by valid ASC
        """,
            varname=varname,
            year_limiter=year_limiter,
        ),
        params,
    )
    units = "°F"
    if varname == "mslp":
        units = "mb"
    elif varname == "vsby":
        units = "mile"
    title = (
        f"{y1 if y1 is not None else ab.year}-"
        f"{y2 if y2 is not None else datetime.now().year} "
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
    ax = fig.add_axes((0.07, 0.1, 0.5, 0.8))

    threshold = timedelta(hours=3)
    reset_valid = datetime(1900, 1, 1, tzinfo=tzinfo)
    xbase = reset_valid

    op2 = operator.lt if mydir == "below" else operator.le
    for row in res.mappings():
        valid: datetime = row["utc_valid"].replace(tzinfo=timezone.utc)
        # This is tricky, we need to resolve when time resets.
        if valid > reset_valid:
            if valids:
                if not plot(ax, xbase, valids, tmpf, lines, tzinfo):
                    break
                valids = []
                tmpf = []
            _tmp = (
                datetime(valid.year, months[-1], 1) + timedelta(days=32)
            ).replace(day=1)
            if month in ["winter", "octmar"]:
                _tmp = _tmp.replace(year=valid.year + 1)
            reset_valid = datetime(_tmp.year, _tmp.month, 1, tzinfo=tzinfo)
            xbase = datetime(valid.year, valid.month, 1, tzinfo=tzinfo)
        if valids and ((valid - valids[-1]) > threshold):
            if not plot(ax, xbase, valids, tmpf, lines, tzinfo):
                break
            valids = []
            tmpf = []
        if operator.ge(row["d"], lower) and op2(row["d"], upper):
            valids.append(valid)
            tmpf.append(row["d"])
        else:
            valids.append(valid)
            tmpf.append(row["d"])
            if not plot(ax, xbase, valids, tmpf, lines, tzinfo):
                break
            valids = []
            tmpf = []

    plot(ax, xbase, valids, tmpf, lines, tzinfo)
    compute_xlabels(ax, xbase)
    rows = []
    for line in lines:
        # Ensure we don't send datetimes to pandas
        rows.append(  # noqa
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
    plot_text(ax, lines)
    return fig, df
