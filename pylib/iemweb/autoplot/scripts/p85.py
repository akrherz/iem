"""
Based on IEM archives of METAR reports, this
application produces the hourly frequency of a temperature at or
above or below a temperature thresold.
"""

import calendar
from datetime import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from sqlalchemy import text

PDICT = {
    "above": "At or Above Temperature",
    "below": "Below Temperature",
}
PDICT2 = {
    "100": "Scale x-axis to 100%",
    "data": "Scale x-axis to Data",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(type="month", name="month", default=7, label="Month:"),
        dict(
            type="int",
            name="t",
            default=80,
            label="Temperature Threshold (F):",
        ),
        dict(
            type="select",
            name="dir",
            default="above",
            label="Threshold Option:",
            options=PDICT,
        ),
        {
            "type": "select",
            "name": "scale",
            "default": "100",
            "label": "Scale X-Axis:",
            "options": PDICT2,
        },
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["zstation"]
    month = int(ctx["month"])
    thres = ctx["t"]
    mydir = ctx["dir"]

    tzname = ctx["_nt"].sts[station]["tzname"]
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text("""
        WITH data as (
            SELECT valid at time zone :tzname  + '10 minutes'::interval as v,
            tmpf
            from alldata where station = :station and tmpf > -90 and tmpf < 150
            and extract(month from valid) = :month and report_type = 3)

        SELECT extract(hour from v) as hour,
        min(v) as min_valid,
        max(v) as max_valid,
        max(case when tmpf::int < :thres THEN v ELSE null END)
            as last_below_valid,
        max(case when tmpf::int >= :thres THEN v ELSE null END)
            as last_above_valid,
        sum(case when tmpf::int < :thres THEN 1 ELSE 0 END) as below,
        sum(case when tmpf::int >= :thres THEN 1 ELSE 0 END) as above,
        count(*) from data
        GROUP by hour ORDER by hour ASC
        """),
            conn,
            params={
                "station": station,
                "month": month,
                "thres": thres,
                "tzname": tzname,
            },
            index_col="hour",
        )
    if df.empty:
        raise NoDataFound("No data found.")

    df["below_freq"] = df["below"].values.astype("f") / df["count"] * 100.0
    df["above_freq"] = df["above"].values.astype("f") / df["count"] * 100.0

    freq = df[mydir + "_freq"].values
    hours = df.index.values
    title = (
        f"({df['min_valid'].min().year} - {df['max_valid'].max().year}) "
        f"{ctx['_sname']}\n"
        f"Frequency of {calendar.month_name[month]} Hour, {PDICT[mydir]}: "
        f"{thres}"
        r"$^\circ$F"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.add_axes((0.45, 0.08, 0.5, 0.75))
    # Add a table of stats
    ax.text(
        0,
        1.02,
        f"Hour | Last {mydir:5s} | Count | Total | Freq",
        ha="right",
        va="bottom",
        transform=ax.transAxes,
    )
    labels = []
    for i, row in df.iterrows():
        dt = row[f"last_{mydir}_valid"]
        dt = "N/A" if pd.isna(dt) else dt.strftime("%d %b %Y")
        hr = datetime(2000, 1, 1, int(i)).strftime("%-I %p")
        labels.append(
            f"{hr:5s} | {dt} | {row[mydir]:,} | "
            f"{row['count']:,} | "
            f"{row[mydir + '_freq']:.1f}%\n"
        )

    ax.barh(hours, freq, fc="blue", align="center")
    ax.set_yticks(range(24))
    ax.set_yticklabels(labels)
    ax.grid(True)
    if ctx["scale"] == "100":
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 5, 25, 50, 75, 95, 100])
    ax.set_xlabel(f"Frequence [%s] (Hour Timezone: {tzname})")
    ax.set_ylim(-0.5, 23.5)

    return fig, df
