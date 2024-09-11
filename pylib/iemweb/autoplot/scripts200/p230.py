"""
This application presents an infographic showing the most recent
date of a given SPC outlook threshold as per IEM unofficial archives.

<p>Note that the probability data can get a little wonky with the changing
usage of levels with time.
"""

from datetime import date, datetime

import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context
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

PDICT = {
    "C": "Convective Categorical",
    "H": "Convective Hail Prob",
    "T": "Convective Tornado Prob",
    "W": "Convective Wind Prob",
    "E": "Excessive Rainfall",
    "F": "Fire Weather",
}
PDICT2 = {
    "all": "Summarize for CONUS",
    "ugc": "Summarize by Selected County/Zone/Parish",
    "state": "Summarize by Selected State",
    "wfo": "Summarize by Selected WFO",
    "fema": "Summarize by FEMA Region",
}
COLORS = {
    "TSTM": "#c0e8c0",
    "MRGL": "#66c57d",
    "SLGT": "#f6f67b",
    "ENH": "#edbf7c",
    "MDT": "#f67a7d",
    "HIGH": "#ff78ff",
    "ELEV": "#ffbb7c",
    "CRIT": "#ff787d",
    "EXTM": "#ff78ff",
    "0.30": "#f67a7d",
    "0.15": "#edbf7c",
}
DAYS = {
    "1": "Day 1",
    "2": "Day 2",
    "3": "Day 3",
    "4": "Day 4",
    "5": "Day 5",
    "6": "Day 6",
    "7": "Day 7",
    "8": "Day 8",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="select",
            name="outlook_type",
            options=PDICT,
            default="C",
            label="Select Outlook Type",
        ),
        dict(
            type="select",
            name="day",
            options=DAYS,
            default="1",
            label="Select Day Outlook",
        ),
        dict(
            type="select",
            name="w",
            options=PDICT2,
            default="wfo",
            label="How to summarize data:",
        ),
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            default="DMX",
            label="Select WFO (when appropriate):",
        ),
        dict(
            type="state",
            name="mystate",
            default="IA",
            label="Select State (when appropriate):",
        ),
        {
            "type": "fema",
            "name": "fema",
            "default": "7",
            "label": "Select FEMA Region (when appropriate):",
        },
        dict(
            type="ugc",
            name="ugc",
            default="IAZ048",
            label="Select UGC Zone/County (when appropriate):",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month(s) Limiter",
            options=MDICT,
        ),
        dict(
            type="date",
            name="date",
            label="Set retroactive date (exclude events on or after date):",
            optional=True,
            default=f"{date.today():%Y/%m/%d}",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    wfo = ctx["wfo"]
    outlook_type = ctx["outlook_type"]
    day = int(ctx["day"])
    ugc = ctx["ugc"]

    params = {
        "day": day,
        "outlook_type": outlook_type if outlook_type in ["F", "E"] else "C",
    }
    date_limiter = ""
    if ctx.get("date") is not None:
        date_limiter = " and outlook_date < :date "
        params["date"] = ctx["date"]
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
    elif month == "octmar":
        months = [10, 11, 12, 1, 2, 3]
    else:
        ts = datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [
            ts.month,
        ]
    if month != "all":
        date_limiter = (
            f" and extract(month from issue) = ANY(:months) {date_limiter}"
        )
    params["months"] = list(months)
    title3 = "" if month == "all" else f" [{MDICT[month]}]"

    sqllimiter = ""
    category = "CATEGORICAL"
    if day >= 4 and outlook_type == "C":
        category = "ANY SEVERE"
    elif day >= 3 and outlook_type == "F":
        category = "CRITICAL FIRE WEATHER AREA"
    elif outlook_type == "F":
        category = "FIRE WEATHER CATEGORICAL"
    elif outlook_type == "H":
        category = "HAIL"
    elif outlook_type == "T":
        category = "TORNADO"
    elif outlook_type == "W":
        category = "WIND"
    params["category"] = category
    if ctx["w"] == "all":
        with get_sqlalchemy_conn("postgis") as conn:
            df = pd.read_sql(
                text(
                    f"""
                with data as (
                select max(expire at time zone 'UTC') as max_expire,
                threshold from spc_outlooks
                WHERE category = :category and day = :day and
                outlook_type = :outlook_type and
                threshold not in ('IDRT', 'SDRT') {date_limiter}
                GROUP by threshold
                )
                select d.* from data d JOIN spc_outlook_thresholds t
                on (d.threshold = t.threshold) ORDER by t.priority desc

            """
                ),
                conn,
                params=params,
                index_col="threshold",
            )
        title2 = "Contiguous US"
    else:
        if ctx["w"] == "wfo":
            table = "cwa"
            abbrcol = "wfo"
            geoval = wfo
            geomcol = "the_geom"
            if wfo not in ctx["_nt"].sts:
                raise NoDataFound("Unknown station metadata.")
            title2 = f"NWS {ctx['_nt'].sts[wfo]['name']} [{wfo}]"
        elif ctx["w"] == "fema":
            table = "fema_regions"
            abbrcol = "region"
            geomcol = "geom"
            geoval = ctx["fema"]
            title2 = f"FEMA Region {geoval}"
        elif ctx["w"] == "ugc":
            table = "ugcs"
            abbrcol = "ugc"
            geomcol = "simple_geom"
            geoval = ugc
            sqllimiter = " and t.end_ts is null "
            cursor = get_dbconn("postgis").cursor()
            cursor.execute(
                "SELECT name from ugcs where ugc = %s and end_ts is null "
                "LIMIT 1",
                (ugc,),
            )
            name = "Unknown"
            if cursor.rowcount == 1:
                name = cursor.fetchone()[0]
            title2 = f"{'County' if ugc[2] == 'C' else 'Zone'} [{ugc}] {name}"
        else:
            table = "states"
            geomcol = "the_geom"
            abbrcol = "state_abbr"
            geoval = ctx["mystate"]
            title2 = state_names[ctx["mystate"]]

        params["geoval"] = geoval
        with get_sqlalchemy_conn("postgis") as conn:
            df = pd.read_sql(
                text(
                    f"""
                    WITH data as (
                select max(expire at time zone 'UTC') as max_expire,
                threshold from
                spc_outlooks o, {table} t
                WHERE t.{abbrcol} = :geoval and category = :category
                and ST_Intersects(st_buffer(o.geom, 0), t.{geomcol})
                and o.day = :day and o.outlook_type = :outlook_type
                {sqllimiter} {date_limiter} GROUP by threshold
                )
                select d.* from data d JOIN spc_outlook_thresholds t
                on (d.threshold = t.threshold) ORDER by t.priority desc
            """
                ),
                conn,
                params=params,
                index_col="threshold",
            )
    conn.close()
    if df.empty:
        raise NoDataFound("No Results For Query.")
    df["date"] = pd.to_datetime(
        df["max_expire"].dt.date - pd.Timedelta(days=1)
    )

    df["days"] = (pd.Timestamp(date.today()) - df["date"]).dt.days
    _ll = ""
    if ctx.get("date") is not None:
        _ll = f"Prior to {ctx['date']:%-d %b %Y}, "
    title = (
        f"{_ll}Most Recent {'WPC' if outlook_type == 'E' else 'SPC'} Day "
        f"{day} {PDICT[outlook_type]} Outlook{title3} for {title2}"
    )
    fig = figure(
        apctx=ctx,
        title=title,
        subtitle="Based on Unofficial IEM Archives.",
    )
    ax = fig.add_axes([0.0, 0.0, 1, 1], frame_on=False)

    ypos = 0.78
    boxheight = 0.12
    rowcount = len(df.index)
    if rowcount > 6:
        boxheight = 0.08
    dmax = max(df["days"].max(), 1)
    for thres, row in df.iterrows():
        if outlook_type in ["C", "F", "E"]:
            if thres not in COLORS:
                continue
            color = COLORS[thres]
        else:
            color = "tan"
        # Outline
        rect = Rectangle(
            (0.02, ypos), 0.94, boxheight - 0.02, ec="k", fc="white"
        )
        ax.add_patch(rect)
        # Box for Label
        rect = Rectangle(
            (0.03, ypos + 0.01), 0.2, boxheight - 0.04, color=color
        )
        ax.add_patch(rect)
        # Overlay label
        fig.text(
            0.1,
            ypos + (boxheight / 2) - 0.01,
            thres,
            fontsize="larger",
            va="center",
            bbox=dict(color="white"),
        )
        # Crude semi-transparent bar underneath
        width = 0.54 * row["days"] / dmax
        rect = Rectangle(
            (0.4, ypos), width, boxheight - 0.02, color=color, alpha=0.3
        )
        ax.add_patch(rect)

        # Days
        fig.text(
            0.3,
            ypos + (boxheight / 2) - 0.01,
            f"{max(0, row['days']):,} Days",
            fontsize="larger",
            va="center",
        )

        # Date
        fig.text(
            0.43,
            ypos + (boxheight / 2) - 0.01,
            row["date"].strftime("%B %-d, %Y"),
            fontsize="larger",
            va="center",
        )
        ypos -= boxheight

    return fig, df.drop(columns=["max_expire"])
