"""x-hour temp change"""
import datetime

import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from sqlalchemy import text

MDICT = {"warm": "Temperature Rise", "cool": "Temperature Drop"}
MDICT2 = dict(
    [
        ("all", "No Month/Time Limit"),
        ("spring", "Spring (MAM)"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("jan", "January"),
        ("feb", "February"),
        ("mar", "March"),
        ("apr", "April"),
        ("may", "May"),
        ("jun", "June"),
        ("jul", "July"),
        ("aug", "August"),
        ("sep", "September"),
        ("oct", "October"),
        ("nov", "November"),
        ("dec", "December"),
    ]
)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This chart presents the largest changes in
    temperature over a given number of hours.  This is based on available
    hourly temperature reports.  It also requires an exact match in time of
    day between two observations.
    """
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(type="int", name="hours", label="Number of Hours:", default=24),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT2,
        ),
        dict(
            type="select",
            name="dir",
            default="warm",
            label="Direction:",
            options=MDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    hours = ctx["hours"]
    mydir = ctx["dir"]
    month = ctx["month"]

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
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    tzname = ctx["_nt"].sts[station]["tzname"]

    # backwards intuitive
    sortdir = "ASC" if mydir == "warm" else "DESC"
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                f"""
        WITH data as (
            SELECT valid, tmpf from alldata
            where station = :station and tmpf between -100 and 150
            and extract(month from valid) in :months),
        doffset as (
            SELECT valid - ':hours hours'::interval as valid, tmpf from data),
        agg as (
            SELECT d.valid, d.tmpf as tmpf1, o.tmpf as tmpf2
            from data d JOIN doffset o on (d.valid = o.valid))
        SELECT valid at time zone 'UTC' as valid1,
        (valid + ':hours hours'::interval) at time zone 'UTC' as valid2,
        tmpf1, tmpf2 from agg ORDER by (tmpf1 - tmpf2) {sortdir} LIMIT 50
        """
            ),
            conn,
            params={
                "station": station,
                "months": tuple(months),
                "hours": hours,
            },
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No database entries found for station, sorry!")

    df["diff"] = (df["tmpf1"] - df["tmpf2"]).abs()
    # Localize the valid times
    for col in ["valid1", "valid2"]:
        # set time zone to UTC
        df[col] = df[col].dt.tz_localize("UTC")
        df[f"local_{col}"] = df[col].dt.tz_convert(tzname)

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']} Top 10 "
        f"{MDICT[mydir]}\n"
        f"Over {hours} Hour Period ({ab.year}-{datetime.date.today().year}) "
        f"[{MDICT2[month]}]"
    )
    fig = figure(title=title, apctx=ctx)
    ax = fig.add_axes([0.45, 0.1, 0.53, 0.8])

    labels = []
    i = 0
    # workaround dups from above
    while i < 50 and len(labels) < 10:
        row = df.iloc[i]
        i += 1
        sts = pd.Timestamp(row["local_valid1"])
        ets = pd.Timestamp(row["local_valid2"])
        lbl = (
            f"{row['tmpf1']:.0f} to {row['tmpf2']:.0f} -> {row['diff']:.0f}\n"
            f"{sts:%-d %b %Y %-I:%M %p} - {ets:%-d %b %Y %-I:%M %p}"
        )
        if lbl in labels:
            continue
        labels.append(lbl)
        ax.barh(len(labels), row["diff"], color="b", align="center")
    ax.set_yticks(range(1, 11))
    ax.set_yticklabels(labels)
    ax.set_ylim(10.5, 0.5)
    ax.grid(True)
    ax.set_xlabel("Delta Degrees Fahrenheit")
    return fig, df


if __name__ == "__main__":
    plotter(
        {"zstation": "IDI", "network": "PA_ASOS", "hours": 1, "dir": "cool"}
    )
