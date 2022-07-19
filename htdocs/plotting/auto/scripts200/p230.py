"""Infographic for last SPC/WPC Outlook of given threshold."""
import datetime

import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.plot import figure
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {
    "C": "Convective",
    "E": "Excessive Rainfall",
    "F": "Fire Weather",
}
PDICT2 = {
    "all": "Summarize for CONUS",
    "ugc": "Summarize by Selected County/Zone/Parish",
    "state": "Summarize by Selected State",
    "wfo": "Summarize by Selected WFO",
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
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This application presents an infographic showing the most recent
    date of a given SPC outlook threshold as per IEM unofficial archives.
    """
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
        dict(
            type="ugc",
            name="ugc",
            default="IAZ048",
            label="Select UGC Zone/County (when appropriate):",
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

    sqllimiter = ""
    category = "CATEGORICAL"
    if day >= 4 and outlook_type == "C":
        category = "ANY SEVERE"
    elif day >= 3 and outlook_type == "F":
        category = "CRITICAL FIRE WEATHER AREA"
    elif outlook_type == "F":
        category = "FIRE WEATHER CATEGORICAL"
    if ctx["w"] == "all":
        with get_sqlalchemy_conn("postgis") as conn:
            df = pd.read_sql(
                """
                select max(expire at time zone 'UTC') as max_expire,
                threshold from spc_outlooks
                WHERE category = %s and day = %s and outlook_type = %s and
                threshold not in ('IDRT', 'SDRT') GROUP by threshold
            """,
                conn,
                params=(
                    category,
                    day,
                    outlook_type,
                ),
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

        with get_sqlalchemy_conn("postgis") as conn:
            df = pd.read_sql(
                f"""
                select max(expire at time zone 'UTC') as max_expire,
                threshold from
                spc_outlooks o, {table} t
                WHERE t.{abbrcol} = %s and category = %s
                and ST_Intersects(st_buffer(o.geom, 0), t.{geomcol})
                and o.day = %s and o.outlook_type = %s {sqllimiter}
                GROUP by threshold
            """,
                conn,
                params=(
                    geoval,
                    category,
                    day,
                    outlook_type,
                ),
                index_col="threshold",
            )
    if df.empty:
        raise NoDataFound("No Results For Query.")
    df["date"] = df["max_expire"].dt.date - datetime.timedelta(days=1)
    df["days"] = (datetime.date.today() - df["date"]).dt.days
    title = (
        f"Most Recent {'WPC' if outlook_type == 'E' else 'SPC'} Day "
        f"{day} {PDICT[outlook_type]} Outlook for {title2}"
    )
    fig = figure(
        apctx=ctx,
        title=title,
        subtitle="Based on Unofficial IEM Archives.",
    )
    ax = fig.add_axes([0.0, 0.0, 1, 1], frame_on=False)

    ypos = 0.78
    dmax = None
    for thres, row in df.sort_values("days", ascending=False).iterrows():
        if thres not in COLORS:
            continue
        if dmax is None:
            dmax = row["days"]
        # Outline
        rect = Rectangle((0.02, ypos), 0.94, 0.1, ec="k", fc="white")
        ax.add_patch(rect)
        # Box for Label
        rect = Rectangle((0.03, ypos + 0.01), 0.2, 0.08, color=COLORS[thres])
        ax.add_patch(rect)
        # Overlay label
        fig.text(
            0.1,
            ypos + 0.05,
            thres,
            fontsize="larger",
            va="center",
            bbox=dict(color="white"),
        )
        # Crude semi-transparent bar underneath
        width = 0.54 * df.at[thres, "days"] / dmax
        rect = Rectangle(
            (0.4, ypos), width, 0.1, color=COLORS[thres], alpha=0.3
        )
        ax.add_patch(rect)

        # Days
        fig.text(
            0.3,
            ypos + 0.05,
            f"{df.at[thres, 'days']:,} Days",
            fontsize="larger",
            va="center",
        )

        # Date
        fig.text(
            0.43,
            ypos + 0.05,
            df.at[thres, "date"].strftime("%B %-d, %Y"),
            fontsize="larger",
            va="center",
        )
        ypos -= 0.12

    return fig, df.drop(columns=["max_expire"])


if __name__ == "__main__":
    plotter({})
