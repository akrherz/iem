"""Based on available hourly observation reports
    by METAR stations, this application presents the top 10 events for a
    given metric of your choice.  Please note that this application often
    reveals bad data stored within the database.  Please do contact us when
    you see suspicious reports and we'll clean up the database.</p>

    <p>You can optionally generate this plot for an explicit period of days,
    the year is ignored with only the month and day portion used.  If you set
    the start date to a date later than the end date, then the effect is to
    consider the date period crossing 1 January.</p>

    <p>If you pick the same start and end date, you effectively get the
    extremes for that date.</p>

    <p>The CSV/Excel download option for this autoplot will return 100
    unfiltered events for further usage as you see fit.</p>
"""
import datetime

import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from sqlalchemy import text

MDICT = {
    "all": "Entire Year",
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

METRICS = dict(
    [
        ("max_tmpf", "Max Air Temperature"),
        ("min_tmpf", "Min Air Temperature"),
        ("below_tmpf", "Air Temperature Below Threshold"),
        ("above_tmpf", "Air Temperature At or Above Threshold"),
        ("min_alti", "Min Pressure Altimeter"),
        ("max_alti", "Max Pressure Altimeter"),
        ("below_alti", "Altimeter Below Threshold"),
        ("above_alti", "Altimeter At or Above Threshold"),
        ("max_dwpf", "Max Dewpoint Temperature"),
        ("min_dwpf", "Min Dewpoint Temperature"),
        ("below_dwpf", "Dewpoint Temperature Below Threshold"),
        ("above_dwpf", "Dewpoint Temperature At or Above Threshold"),
        ("max_feel", "Max Feels Like Temperature"),
        ("min_feel", "Min Feels Like Temperature"),
        ("below_feel", "Feels Like Temperature Below Threshold"),
        ("above_feel", "Feels Like Temperature At or Above Threshold"),
        ("max_p01i", "Max Hourly Precipitation"),
        ("above_p01i", "Precipitation At or Above Threshold"),
        ("min_mslp", "Min Sea Level Pressure"),
        ("max_mslp", "Max Sea Level Pressure"),
        ("below_mslp", "Sea Level Pressure Below Threshold"),
        ("above_mslp", "Sea Level Pressure At or Above Threshold"),
        ("max_sknt", "Max Wind Speed Sustained"),
        ("max_gust", "Max Wind Speed Gust"),
    ]
)
UNITS = {
    "tmpf": "F",
    "dwpf": "F",
    "feel": "F",
    "p01i": "inch",
    "mslp": "hPa",
    "alti": "inch",
    "sknt": "knots",
    "gust": "knots",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="var",
            default="max_p01i",
            label="Which Metric to Summarize",
            options=METRICS,
        ),
        dict(
            type="float",
            name="threshold",
            default=100,
            label="Set Threshold (where appropriate for metric above)",
        ),
        dict(
            type="hour",
            name="hour",
            optional=True,
            label="Limit Analysis to Given Local Timezone Hour (optional)",
            default=12,
        ),
        dict(
            type="sday",
            name="sdate",
            default="0101",
            optional=True,
            label=(
                "Start date (inclusive) for explicit date period: (optional)"
            ),
        ),
        dict(
            type="sday",
            name="edate",
            default="1231",
            optional=True,
            label="End date (inclusive) for explicit date period: (optional)",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    month = ctx["month"]
    varname = ctx["var"]
    tzname = ctx["_nt"].sts[station]["tzname"]
    params = {}
    params["station"] = station
    params["tzname"] = tzname
    if ctx.get("sdate") and ctx.get("edate"):
        op = "or" if ctx["sdate"] > ctx["edate"] else "and"
        date_limiter = (
            " and (to_char(valid at time zone :tzname, 'mmdd') >= :ssday "
            f" {op} to_char(valid at time zone :tzname, 'mmdd') <= :esday)"
        )
        params["ssday"] = ctx["sdate"].strftime("%m%d")
        params["esday"] = ctx["edate"].strftime("%m%d")
        title2 = f"between {ctx['sdate']:%-d %b} and {ctx['edate']:%-d %b}"
        if ctx["sdate"] == ctx["edate"]:
            date_limiter = (
                "and to_char(valid at time zone :tzname, 'mmdd') = :ssday "
            )
            title2 = f"on {ctx['sdate']:%-d %b}"
    else:
        if month == "all":
            months = range(1, 13)
        elif month == "fall":
            months = [9, 10, 11]
        elif month == "winter":
            months = [12, 1, 2]
        elif month == "spring":
            months = [3, 4, 5]
        elif month == "summer":
            months = [6, 7, 8]
        elif month == "octmar":
            months = [10, 11, 12, 1, 2, 3]
        else:
            ts = datetime.datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
            # make sure it is length two for the trick below in SQL
            months = [ts.month, 999]
        date_limiter = (
            " and extract(month from valid at time zone :tzname) in :months "
        )
        params["months"] = tuple(months)
        title2 = MDICT[month]
    if ctx.get("hour") is not None:
        date_limiter += (
            " and extract(hour from valid at time zone :tzname "
            "+ '10 minutes'::interval) = :hour "
        )
        params["hour"] = ctx["hour"]
        dt = datetime.datetime(2000, 1, 1, ctx["hour"])
        title2 += f" @{dt:%-I %p}"
    (agg, dbvar) = varname.split("_")
    # Special accounting for the peak_wind_gust column
    if dbvar == "gust":
        titlelabel = "Top"
        with get_sqlalchemy_conn("asos") as conn:
            df = pd.read_sql(
                text(
                    f"""
                WITH data as (
                    SELECT
                    case when peak_wind_gust > gust then peak_wind_time
                    else valid end as v,
                    case when peak_wind_gust > gust then peak_wind_gust
                    else gust end as speed from alldata
                    WHERE station = :station {date_limiter})

                SELECT v at time zone :tzname as valid, speed as gust from data
                WHERE speed is not null
                ORDER by gust DESC LIMIT 100
            """
                ),
                conn,
                params=params,
                index_col=None,
            )

    elif agg in ["max", "min"]:
        titlelabel = "Top"
        sorder = "DESC" if agg == "max" else "ASC"
        with get_sqlalchemy_conn("asos") as conn:
            df = pd.read_sql(
                text(
                    f"""
                WITH data as (
                    SELECT valid at time zone :tzname as v, {dbvar}
                    from alldata WHERE station = :station {date_limiter})

                SELECT v as valid, {dbvar} from data
                ORDER by {dbvar} {sorder} NULLS LAST LIMIT 100
            """
                ),
                conn,
                params=params,
                index_col=None,
            )
    else:
        titlelabel = "Most Recent"
        op = ">=" if agg == "above" else "<"
        threshold = float(ctx.get("threshold", 100))
        with get_sqlalchemy_conn("asos") as conn:
            df = pd.read_sql(
                text(
                    f"SELECT valid at time zone :tzname as valid, "
                    f"{dbvar} from "
                    f"alldata WHERE station = :station {date_limiter} and "
                    f"{dbvar} {op} {threshold} "
                    "ORDER by valid DESC LIMIT 100"
                ),
                conn,
                params=params,
                index_col=None,
            )
    if df.empty:
        raise NoDataFound("Error, no results returned!")
    ylabels = []
    fmt = "%.0f" if dbvar in ["tmpf", "dwpf", "sknt", "gust"] else "%.2f"
    hours = []
    y = []
    lastval = -99
    ranks = []
    currentrank = 0
    rows2keep = []
    for idx, row in df.iterrows():
        key = row["valid"].strftime("%Y%m%d%H")
        if key in hours or pd.isnull(row[dbvar]):
            continue
        rows2keep.append(idx)
        hours.append(key)
        y.append(row[dbvar])
        lbl = fmt % (row[dbvar],)
        lbl += f" -- {row['valid']:%b %d, %Y %-I:%M %p}"
        ylabels.append(lbl)
        if row[dbvar] != lastval or agg in ["above", "below"]:
            currentrank += 1
        ranks.append(currentrank)
        lastval = row[dbvar]
        if len(ylabels) == 10:
            break
    if not y:
        raise NoDataFound("No data found.")

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    title = f"{ctx['_sname']} {titlelabel} 10 Events"
    st = ctx.get("threshold") if agg in ["above", "below"] else ""
    subtitle = (
        f"{METRICS[varname]} {st} ({title2}) "
        f"({ab.year}-{datetime.datetime.now().year})"
    )
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    ax = fig.add_axes([0.1, 0.1, 0.65, 0.8])
    ax.barh(
        range(len(y), 0, -1),
        y,
        ec="green",
        fc="green",
        height=0.8,
        align="center",
    )
    ax2 = ax.twinx()
    ax2.set_ylim(0.5, 10.5)
    ax.set_ylim(0.5, 10.5)
    ax2.set_yticks(range(1, len(y) + 1))
    ax.set_yticks(range(1, len(y) + 1))
    ax.set_yticklabels([f"#{x}" for x in ranks][::-1])
    ax2.set_yticklabels(ylabels[::-1])
    ax.grid(True, zorder=11)
    ax.set_xlabel(f"{METRICS[varname]} {UNITS[dbvar]}")
    fig.text(
        0.98,
        0.03,
        f"Timezone: {tzname}",
        ha="right",
        fontsize=14,
    )

    return fig, df


if __name__ == "__main__":
    plotter({})
