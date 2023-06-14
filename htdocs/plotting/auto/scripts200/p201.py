"""
This application presents a calendar of Storm Prediction Center or Weather
Prediction Center outlooks by state, WFO, or county. The GIS spatial operation
done is a simple touches.  So an individual outlook that just barely
scrapes the selected area would count for this presentation.  Suggestions
would be welcome as to how this could be improved.

<p>This app attempts to not double-count outlook days.  A SPC/WPC Outlook
technically crosses two calendar days ending at 12 UTC (~7 AM). This
application considers the midnight to ~7 AM period to be for the
previous day, which is technically not accurate but the logic that most
people expect to see.</p>
"""
import calendar
import datetime

import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator
from pyiem.exceptions import NoDataFound
from pyiem.plot import calendar_plot, figure
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, get_dbconn, get_sqlalchemy_conn

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
PDICT3 = {"yes": "Yes", "no": "No"}
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
MDICT = {
    "cal": "Plot Calendar (limited <= 12 months)",
    "heat": "Plot Heatmap (unlimited)",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    jan1 = today.replace(month=1, day=1)
    desc["arguments"] = [
        dict(
            type="select",
            name="mode",
            default="cal",
            label="Plotting Mode:",
            options=MDICT,
        ),
        dict(
            type="date",
            name="sdate",
            default=jan1.strftime("%Y/%m/%d"),
            label="Start Date (inclusive):",
            min="1987/01/01",
        ),
        dict(
            type="date",
            name="edate",
            default=today.strftime("%Y/%m/%d"),
            max=(today + datetime.timedelta(days=8)).strftime("%Y/%m/%d"),
            label="End Date (inclusive):",
            min="1987/01/01",
        ),
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
        dict(
            type="select",
            options=PDICT3,
            default="yes",
            name="g",
            label="Include TSTM (general thunder) in generated calendar?",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    sts = ctx["sdate"]
    ets = ctx["edate"]
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
            with data as (
                select outlook_date, threshold from spc_outlooks
                WHERE category = %s and day = %s and outlook_type = %s and
                outlook_date >= %s and outlook_date <= %s and
                threshold not in ('IDRT', 'SDRT')),
            agg as (
                select outlook_date, d.threshold, priority,
                rank() OVER (PARTITION by outlook_date ORDER by priority DESC)
                from data d JOIN spc_outlook_thresholds t
                on (d.threshold = t.threshold))

            SELECT distinct outlook_date as date, threshold from agg
            where rank = 1 ORDER by date ASC
            """,
                conn,
                params=(
                    category,
                    day,
                    outlook_type,
                    sts,
                    ets + datetime.timedelta(days=2),
                ),
                index_col="date",
                parse_dates=[
                    "date",
                ],
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
            with data as (
                select outlook_date, threshold from
                spc_outlooks o, {table} t
                WHERE t.{abbrcol} = %s and category = %s
                and ST_Intersects(st_buffer(o.geom, 0), t.{geomcol})
                and o.day = %s and o.outlook_type = %s and outlook_date >= %s
                and outlook_date <= %s {sqllimiter}),
            agg as (
                select outlook_date, d.threshold, priority,
                rank() OVER (PARTITION by outlook_date ORDER by priority DESC)
                from data d JOIN spc_outlook_thresholds t
                on (d.threshold = t.threshold))

            SELECT distinct outlook_date as date, threshold from agg
            where rank = 1 ORDER by date ASC
            """,
                conn,
                params=(
                    geoval,
                    category,
                    day,
                    outlook_type,
                    sts,
                    ets + datetime.timedelta(days=2),
                ),
                index_col="date",
                parse_dates=[
                    "date",
                ],
            )

    data = {}
    now = sts
    while now <= ets:
        data[now] = {"val": " "}
        now += datetime.timedelta(days=1)
    aggtxt = []
    if not df.empty:
        df2 = (
            df.reset_index()
            .groupby("threshold")
            .last()
            .assign(
                days=lambda df_: (pd.Timestamp(ets) - df_["date"]).dt.days,
            )
        )
        for thres, row in df2.iterrows():
            if thres in COLORS:
                aggtxt.append(f"{thres} {row['days']} Days")
    for date, row in df.iterrows():
        if row["threshold"] == "TSTM" and ctx.get("g", "yes") == "no":
            continue
        data[date.to_pydatetime().date()] = {
            "val": row["threshold"],
            "cellcolor": COLORS.get(row["threshold"], "#EEEEEE"),
        }
    title = (
        f"Highest {'WPC' if outlook_type == 'E' else 'SPC'} Day "
        f"{day} {PDICT[outlook_type]} Outlook for {title2}"
    )
    subtitle = (
        f"Valid {sts:%d %b %Y} - {ets:%d %b %Y}. "
        f"Days since by threshold: {', '.join(aggtxt)}"
    )
    if ctx["mode"] == "cal":
        fig = calendar_plot(
            sts,
            ets,
            data,
            apctx=ctx,
            title=title,
            subtitle=subtitle,
        )
    else:
        fig = figure(apctx=ctx, title=title, subtitle=subtitle)
        ax = fig.add_axes([0.05, 0.15, 0.9, 0.75])
        data = np.ones((ets.year - sts.year + 1, 366)) * -1
        thresholds = list(COLORS.keys())
        for date, row in df.iterrows():
            if date > pd.Timestamp(ets):
                continue
            if row["threshold"] == "TSTM" and ctx.get("g", "yes") == "no":
                continue
            if row["threshold"] in thresholds:
                y = date.year - sts.year
                x = int(date.strftime("%j"))
                data[y, x - 1] = thresholds.index(row["threshold"])

        cmap = mpcolors.ListedColormap(list(COLORS.values()))
        cmap.set_under("#FFF")
        norm = mpcolors.BoundaryNorm(range(len(COLORS)), cmap.N)
        ax.imshow(
            data,
            aspect="auto",
            interpolation="nearest",
            extent=(0, 366, ets.year + 0.5, sts.year - 0.5),
            cmap=cmap,
            norm=norm,
        )
        rects = []
        rlabels = []
        uvals = df["threshold"].unique().tolist()
        for thres, color in COLORS.items():
            if thres in uvals:
                rlabels.append(thres)
                rects.append(Rectangle((0, 0), 1, 1, fc=color))
        ax.legend(
            rects,
            rlabels,
            ncol=10,
            loc=(0, -0.1),
        )
        ax.set_xticks([0, 30, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334])
        ax.set_xticklabels(calendar.month_abbr[1:])
        ax.grid()
        ax.yaxis.set_major_locator(MaxNLocator(min_n_ticks=1, integer=True))

    return fig, df


if __name__ == "__main__":
    plotter(
        dict(
            mode="heat",
            state="IA",
            w="all",
            sdate="2021-01-01",
            day="1",
            edate="2021-09-21",
        )
    )
