"""Plot SPC Outlook Infographics."""
import datetime

# third party
import pandas as pd
from geopandas import read_postgis
import cartopy.crs as ccrs
from matplotlib.patches import Rectangle
from pyiem.plot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn, utc
from pyiem.exceptions import NoDataFound
from pyiem.reference import Z_OVERLAY2_LABEL, Z_POLITICAL

PDICT = {
    "cwa": "Plot by NWS Forecast Office",
    "state": "Plot by State/Sector",
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


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 600
    desc[
        "description"
    ] = """
    This app generates infographics for the Storm Prediction Center
    outlooks.  The trick here is how the valid time works.  The app will first
    attempt to match an issuance to that timestamp, if it fails, it then
    looks backwards in time for the most recent issuance to that timestamp.

    <p>Another bit of ambiguity is which outlook you get between about
    midnight and the 12z issuance of the Day 1 Outlook.  In this case and
    as the code stands now, you get the next day's outlook.
    """
    desc["arguments"] = [
        dict(
            type="select",
            default="1C",
            name="which",
            options=PDICT2,
            label="Select SPC Outlook Day and Type",
        ),
        dict(
            type="select",
            default="categorical",
            name="cat",
            options=PDICT3,
            label="Select SPC Outlook Category",
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
            label="Select WFO: (ignored if plotting state)",
        ),
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
            min="2002/01/01 0000",
        ),
    ]
    return desc


def outlook_search(pgconn, valid, days, outlook_type):
    """Go look for a nearest in time TAF."""
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT product_issue at time zone 'UTC' from spc_outlook "
        "WHERE day in %s and outlook_type = %s and product_issue > %s and "
        "product_issue < %s ORDER by product_issue DESC",
        (days, outlook_type, valid - datetime.timedelta(hours=24), valid),
    )
    if cursor.rowcount == 0:
        return None
    return cursor.fetchone()[0].replace(tzinfo=datetime.timezone.utc)


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    valid = ctx["valid"].replace(tzinfo=datetime.timezone.utc)
    pgconn = get_dbconn("postgis")
    day, outlook_type = int(ctx["which"][0]), ctx["which"][1]
    category = ctx["cat"].upper()
    if outlook_type == "F":
        category = "FIRE WEATHER CATEGORICAL"
    if (day == 0 or day > 2) and outlook_type == "F":
        category = "CRITICAL FIRE WEATHER AREA"
    if (day == 0 or day > 3) and outlook_type == "C":
        category = "ANY SEVERE"
    days = (day,)
    if day == 0:
        days = tuple(range(4, 9))
        if outlook_type == "F":
            days = tuple(range(3, 9))

    def fetch(ts):
        """Getme data."""
        return read_postgis(
            "SELECT o.*, g.*, t.priority from spc_outlook o, "
            "spc_outlook_geometries g, spc_outlook_thresholds t WHERE "
            "o.id = g.spc_outlook_id and g.threshold = t.threshold and "
            "product_issue = %s and day in %s and category = %s and "
            "outlook_type = %s ORDER by o.day ASC, t.priority ASC",
            pgconn,
            params=(ts, days, category, outlook_type),
            index_col=None,
            geom_col="geom",
        )

    df = fetch(valid)
    if df.empty:
        valid = outlook_search(pgconn, valid, days, outlook_type)
        if valid is None:
            raise NoDataFound("SPC Outlook data was not found!")
        df = fetch(valid)
    if ctx["t"] == "cwa":
        sector = "cwa"
    else:
        sector = "state" if len(ctx["csector"]) == 2 else ctx["csector"]
    daylabel = day if day > 0 else "%s-%s" % (days[0], days[-1])
    mp = MapPlot(
        title=(
            f"Storm Prediction Center Day {daylabel} {category.capitalize()}"
        ),
        subtitle=(
            f"Issued: {df.iloc[0]['product_issue'].strftime(ISO)} UTC "
            f"Valid: {df['issue'].min().strftime(ISO)} UTC "
            f"Expire: {df['expire'].max().strftime(ISO)} UTC"
        ),
        sector=sector,
        twitter=True,
        state=ctx["csector"],
        cwa=(ctx["wfo"] if len(ctx["wfo"]) == 3 else ctx["wfo"][1:]),
        nocaption=True,
    )
    rects = []
    rectlabels = []
    for _idx, row in df.iterrows():
        if row["threshold"] == "SIGN":
            mp.ax.add_geometries(
                [row["geom"]],
                ccrs.PlateCarree(),
                facecolor="None",
                edgecolor="k",
                linewidth=2,
                hatch="/",
                zorder=Z_POLITICAL - 1,
            )
            rect = Rectangle((0, 0), 1, 1, fc="None", hatch="/")
        else:
            fc = COLORS[row["threshold"]]
            ec = OUTLINE_COLORS.get(row["threshold"], "k")
            if day == 0:
                fc, ec = "None", DAY_COLORS[row["day"]]
                if row["threshold"] == "0.30":
                    fc, ec = ec, ec
            mp.ax.add_geometries(
                [row["geom"]],
                ccrs.PlateCarree(),
                facecolor=fc,
                edgecolor=ec,
                linewidth=2,
                zorder=Z_POLITICAL - 1,
            )
            rect = Rectangle((0, 0), 1, 1, fc=fc, ec=ec)
        rects.append(rect)
        label = THRESHOLD_LEVELS.get(row["threshold"], row["threshold"])
        if day == 0:
            label = f"D{row['day']} {label}"
        rectlabels.append(label)
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

    if sector == "cwa":
        mp.draw_cwas(color="k", linewidth=2.5)
        mp.drawcounties()
        mp.drawcities()

    for col in ["product_issue", "issue", "expire", "updated"]:
        # some rows could be NaN
        df[col] = df[~pd.isna(df[col])][col].apply(lambda x: x.strftime(ISO))
    return mp.fig, df.drop("geom", axis=1)


if __name__ == "__main__":
    # has all 5 days with something included
    # plotter(dict(cat="categorical", which="0C", valid="2019-05-14 2022"))
    # has three days of F
    plotter(dict(cat="categorical", which="0F", valid="2018-05-07 2322"))
