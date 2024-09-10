"""
This app generates infographics for the Storm Prediction Center
or Weather Prediction Center outlooks.
The trick here is how the valid time works.  The app will first
attempt to match an issuance to that timestamp, if it fails, it then
looks backwards in time for the most recent issuance to that timestamp.

<p>Another bit of ambiguity is which outlook you get between about
midnight and the 13z issuance of the Day 1 Outlook.  In this case and
as the code stands now, you get the next day's outlook.

<p>A <a href="/request/gis/outlooks.phtml">GIS Shapefile</a> download
option exists for downloading these outlooks in-bulk.</p>
"""

import datetime
from zoneinfo import ZoneInfo

# third party
import pandas as pd
from geopandas import read_postgis
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot
from pyiem.reference import LATLON, Z_OVERLAY2_LABEL, Z_POLITICAL
from pyiem.util import get_autoplot_context, utc
from sqlalchemy import text

CENTRALTZ = ZoneInfo("America/Chicago")
PDICT = {
    "cwa": "Plot by NWS Forecast Office",
    "state": "Plot by State/Sector",
    "fema": "Plot by FEMA Region",
}
PDICT2 = {
    "1C": "Day 1 Convective",
    "2C": "Day 2 Convective",
    "3C": "Day 3 Convective",
    "4C": "Day 4 Convective",
    "5C": "Day 5 Convective",
    "6C": "Day 6 Convective",
    "7C": "Day 7 Convective",
    "8C": "Day 8 Convective",
    "0C": "Day 4-8 Convective",
    "1F": "Day 1 Fire Weather",
    "2F": "Day 2 Fire Weather",
    "0F": "Day 3-8 Fire Weather",
    "1E": "Day 1 Excessive Rainfall Outlook",
    "2E": "Day 2 Excessive Rainfall Outlook",
    "3E": "Day 3 Excessive Rainfall Outlook",
    "4E": "Day 4 Excessive Rainfall Outlook",
    "5E": "Day 5 Excessive Rainfall Outlook",
}
PDICT3 = {
    "categorical": "Categorical (D1-3), Any Severe (D4-8)",
    "hail": "Hail (D1-2)",
    "tornado": "Tornado (D1-2)",
    "wind": "Wind (D1-2)",
}
THRESHOLD_LEVELS = {
    "TSTM": "Thunderstorms",
    "MRGL": "1. Marginal",
    "SLGT": "2. Slight",
    "ENH": "3. Enhanced",
    "MDT": "4. Moderate",
    "HIGH": "5. High",
}
# Overrides the above
WPC_THRESHOLD_LEVELS = {
    "MDT": "3. Moderate",
    "HIGH": "4. High",
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
    "IDRT": "#c5a392",
    "SDRT": "#ff7f7f",
    "0.02": "#008b00",
    "0.05": "#8b4726",
    "0.10": "#ffc800",
    "0.15": "#ff0000",
    "0.30": "#ff00ff",
    "0.45": "#912cee",
    "0.60": "#104e8b",
}
DAY_COLORS = {
    3: "#ff00ff",
    4: "#ff0000",
    5: "#ffff00",
    6: "#edbf7c",
    7: "#f67a7d",
    8: "#ff78ff",
}
OUTLINE_COLORS = {
    "TSTM": "#566453",
    "MRGL": "#437a43",
    "SLGT": "#d8a31f",
    "ENH": "#d9921c",
    "MDT": "#a6160b",
    "HIGH": "#d21fc3",
}
ISO = "%Y-%m-%d %H:%M"
SQL = """
WITH data as (
    SELECT o.*, g.* from spc_outlook o LEFT JOIN spc_outlook_geometries g
    on (o.id = g.spc_outlook_id and g.category = :c) WHERE product_issue = :ts
    and day = ANY(:days) and outlook_type = :ot)

SELECT d.product_issue at time zone 'UTC' as product_issue,
expire at time zone 'UTC' as expire, d.geom,
issue at time zone 'UTC' as issue, d.threshold,
updated at time zone 'UTC' as updated, d.product_id, d.day,
d.cycle, d.outlook_type, t.priority from data d LEFT JOIN
spc_outlook_thresholds t on (d.threshold = t.threshold)
ORDER by day ASC, priority ASC
"""


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["defaults"] = {"_r": "t"}
    desc["cache"] = 600
    desc["arguments"] = [
        dict(
            type="select",
            default="1C",
            name="which",
            options=PDICT2,
            label="Select SPC/WPC Outlook Day and Type",
        ),
        dict(
            type="select",
            default="categorical",
            name="cat",
            options=PDICT3,
            label="Select SPC/WPC Outlook Category",
        ),
        dict(
            type="select",
            name="t",
            default="state",
            options=PDICT,
            label="Select plot extent type:",
        ),
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            default="DMX",
            label="Select WFO: (when applicable)",
        ),
        {
            "type": "fema",
            "default": "7",
            "name": "fema",
            "label": "Select FEMA Region (when applicable):",
        },
        dict(
            type="csector",
            name="csector",
            default="IA",
            label="Select state/sector to plot",
        ),
        dict(
            type="datetime",
            name="valid",
            default=utc().strftime("%Y/%m/%d %H%M"),
            label="Outlook Issuance/Valid Timestamp (UTC Timezone):",
            min="1987/01/01 0000",
        ),
    ]
    return desc


def outlook_search(valid, days, outlook_type):
    """Find nearest outlook."""
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text("""
                 SELECT product_issue at time zone 'UTC' from spc_outlook
            WHERE day = ANY(:days) and outlook_type = :ot
            and product_issue > :sts and
            product_issue < :ets ORDER by product_issue DESC
            """),
            {
                "days": days,
                "ot": outlook_type,
                "sts": valid - datetime.timedelta(hours=24),
                "ets": valid,
            },
        )
        if res.rowcount == 0:
            return None
        return res.fetchone()[0].replace(tzinfo=datetime.timezone.utc)


def compute_datelabel(df):
    """Figure out something pretty."""
    # Woof
    date1 = df["issue"].min().to_pydatetime().astimezone(CENTRALTZ)
    date2 = df["issue"].max().to_pydatetime().astimezone(CENTRALTZ)
    if date1 == date2:
        return date1.strftime("%B %-d, %Y")
    if date1.month == date2.month:
        return (
            date1.strftime("%B %-d-")
            + date2.strftime("%-d ")
            + str(date2.year)
        )
    return (
        date1.strftime("%b %-d-") + date2.strftime("%b %-d ") + str(date2.year)
    )


def get_threshold_label(threshold, outlook_type):
    """Make it pretty."""
    if threshold in THRESHOLD_LEVELS:
        if outlook_type == "E":
            return WPC_THRESHOLD_LEVELS.get(
                threshold,
                THRESHOLD_LEVELS[threshold],
            )
        return THRESHOLD_LEVELS[threshold]
    if threshold.startswith("0."):
        return f"{(float(threshold) * 100.0):.0f}%"
    return threshold


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    valid = ctx["valid"].replace(tzinfo=datetime.timezone.utc)
    day, outlook_type = int(ctx["which"][0]), ctx["which"][1]
    category = ctx["cat"].upper()
    # Ensure we don't have an incompatable combo
    if outlook_type == "E":
        category = "CATEGORICAL"
    elif outlook_type == "F":
        category = "FIRE WEATHER CATEGORICAL"
    if (day == 0 or day > 2) and outlook_type == "F":
        category = "CRITICAL FIRE WEATHER AREA"
    if (day == 0 or day > 3) and outlook_type == "C":
        category = "ANY SEVERE"
    days = [
        day,
    ]
    if day == 0:
        days = list(range(4, 9))
        if outlook_type == "F":
            days = list(range(3, 9))

    def fetch(ts):
        """Getme data."""
        # NB careful here with the joins and not to use the view!
        with get_sqlalchemy_conn("postgis") as conn:
            df = read_postgis(
                text(SQL),
                conn,
                params={
                    "c": category,
                    "ts": ts,
                    "days": days,
                    "ot": outlook_type,
                },
                index_col=None,
                geom_col="geom",
            )
        return df

    df = fetch(valid)
    if df.empty:
        valid = outlook_search(valid, days, outlook_type)
        if valid is None:
            raise NoDataFound("SPC Outlook data was not found!")
        df = fetch(valid)
    for col in ["updated", "product_issue", "issue", "expire"]:
        df[col] = df[col].dt.tz_localize(datetime.timezone.utc)
    csector = ctx.pop("csector")
    if ctx["t"] == "cwa":
        sector = "cwa"
    elif ctx["t"] == "fema":
        sector = "fema_region"
    else:
        sector = "state" if len(csector) == 2 else csector
    daylabel = day if day > 0 else f"{days[0]}-{days[-1]}"
    datelabel = compute_datelabel(df)

    catlabel = " ".join([x.capitalize() for x in category.split()])
    w = "Weather" if outlook_type == "E" else "Storm"
    if outlook_type == "E":
        catlabel = "Excessive Rainfall"
    mp = MapPlot(
        apctx=ctx,
        title=(
            f"{datelabel} {w} Prediction Center Day {daylabel} "
            f"{catlabel} Outlook"
        ),
        subtitle=(
            f"Issued: {df.iloc[0]['product_issue'].strftime(ISO)} UTC "
            f"| Valid: {df['issue'].min().strftime(ISO)} UTC "
            f"| Expire: {df['expire'].max().strftime(ISO)} UTC"
        ),
        sector=sector,
        state=csector,
        cwa=(ctx["wfo"] if len(ctx["wfo"]) == 3 else ctx["wfo"][1:]),
        fema_region=ctx["fema"],
        nocaption=True,
        background="ne2",
    )
    rects = []
    rectlabels = []
    for _idx, row in df[~pd.isna(df["threshold"])].iterrows():
        if row["threshold"] == "SIGN":
            mp.panels[0].add_geometries(
                [row["geom"]],
                LATLON,
                facecolor="None",
                edgecolor="k",
                linewidth=2,
                hatch="/",
                zorder=Z_POLITICAL - 1,
            )
            rect = Rectangle((0, 0), 1, 1, fc="None", hatch="/")
        else:
            fc = COLORS.get(row["threshold"], "red")
            ec = OUTLINE_COLORS.get(row["threshold"], "k")
            if day > 3 and row["threshold"] in ["0.15", "0.30"]:
                _xref = {"0.15": "SLGT", "0.30": "ENH"}
                fc = COLORS[_xref[row["threshold"]]]
                ec = OUTLINE_COLORS[_xref[row["threshold"]]]
            if day == 0:
                fc, ec = "None", DAY_COLORS[row["day"]]
                if row["threshold"] == "0.30":
                    fc = ec
            mp.panels[0].add_geometries(
                [row["geom"]],
                LATLON,
                facecolor=fc,
                edgecolor=ec,
                linewidth=2,
                zorder=Z_POLITICAL - 1,
            )
            rect = Rectangle((0, 0), 1, 1, fc=fc, ec=ec)
        rects.append(rect)
        label = get_threshold_label(row["threshold"], outlook_type)
        if day == 0:
            label = f"D{row['day']} {label}"
        rectlabels.append(label)
    if rects:
        mp.ax.legend(
            rects,
            rectlabels,
            ncol=1,
            loc="lower right",
            fontsize=12,
            bbox_to_anchor=(1.08, 0.01),
            fancybox=True,
            framealpha=1,
        ).set_zorder(Z_OVERLAY2_LABEL + 100)
    else:
        emptytext = "Potential Too Low"
        if (
            outlook_type == "C"
            and day in [1, 2, 3]
            and category == "categorical"
        ):
            emptytext = "No Thunderstorms Forecast"
        mp.ax.text(
            0.5,
            0.5,
            emptytext,
            transform=mp.ax.transAxes,
            fontsize=30,
            ha="center",
            color="yellow",
            bbox=dict(color="black", alpha=0.5),
            zorder=Z_OVERLAY2_LABEL,
        )

    if sector == "cwa":
        mp.draw_cwas(color="k", linewidth=2.5)
    if sector == "fema_region":
        mp.draw_fema_regions()
    if sector in ["cwa", "state"]:
        mp.drawcounties()
        mp.drawcities()

    for col in ["product_issue", "issue", "expire", "updated"]:
        # some rows could be NaN
        df[col] = df[~pd.isna(df[col])][col].apply(lambda x: x.strftime(ISO))
    return mp.fig, df.drop("geom", axis=1)
