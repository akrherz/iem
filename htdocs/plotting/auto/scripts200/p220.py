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

PDICT = {"cwa": "Plot by NWS Forecast Office", "state": "Plot by State"}
PDICT2 = {
    "1C": "Day 1 Convective",
    "2C": "Day 2 Convective",
    "3C": "Day 3 Convective",
    "4C": "Day 4 Convective",
    "5C": "Day 5 Convective",
    "6C": "Day 6 Convective",
    "7C": "Day 7 Convective",
    "8C": "Day 8 Convective",
    "1F": "Day 1 Fire Weather",
    "2F": "Day 2 Fire Weather",
    "3F": "Day 3 Fire Weather",
}
PDICT3 = {
    "categorical": "Categorical (D1-3), Any Severe (D4-8)",
    "hail": "Hail (D1-2)",
    "tornado": "Tornado (D1-2)",
    "wind": "Wind (D1-2)",
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


def outlook_search(pgconn, valid, day, outlook_type):
    """Go look for a nearest in time TAF."""
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT product_issue at time zone 'UTC' from spc_outlooks "
        "WHERE day = %s and outlook_type = %s and product_issue > %s and "
        "product_issue < %s ORDER by product_issue DESC",
        (day, outlook_type, valid - datetime.timedelta(hours=24), valid),
    )
    if cursor.rowcount == 0:
        return None
    return cursor.fetchone()[0].replace(tzinfo=datetime.timezone.utc)


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    valid = ctx["valid"].replace(tzinfo=datetime.timezone.utc)
    pgconn = get_dbconn("postgis")
    day, outlook_type = ctx["which"][0], ctx["which"][1]
    category = ctx["cat"].upper()
    if outlook_type == "F":
        category = "FIRE WEATHER CATEGORICAL"
    if int(day) > 3 and outlook_type == "C":
        category = "ANY SEVERE"

    def fetch(ts):
        """Getme data."""
        return read_postgis(
            "SELECT o.*, g.*, t.priority from spc_outlook o, "
            "spc_outlook_geometries g, spc_outlook_thresholds t WHERE "
            "o.id = g.spc_outlook_id and g.threshold = t.threshold and "
            "product_issue = %s and day = %s and category = %s and "
            "outlook_type = %s ORDER by t.priority ASC",
            pgconn,
            params=(ts, day, category, outlook_type),
            index_col=None,
            geom_col="geom",
        )

    df = fetch(valid)
    if df.empty:
        valid = outlook_search(pgconn, valid, day, outlook_type)
        if valid is None:
            raise NoDataFound("SPC Outlook data was not found!")
        df = fetch(valid)
    if ctx["t"] == "cwa":
        sector = "cwa"
    else:
        sector = "state" if len(ctx["csector"]) == 2 else ctx["csector"]
    mp = MapPlot(
        title=f"Storm Prediction Center Day {day} {category.capitalize()}",
        subtitle=(
            f"Issued: {df.iloc[0]['product_issue'].strftime(ISO)} UTC "
            f"Valid: {df.iloc[0]['issue'].strftime(ISO)} UTC "
            f"Expire: {df.iloc[0]['expire'].strftime(ISO)} UTC"
        ),
        sector=sector,
        twitter=True,
        state=ctx["csector"],
        cwa=(ctx["wfo"] if len(ctx["wfo"]) == 3 else ctx["wfo"][1:]),
    )
    rects = []
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
            mp.ax.add_geometries(
                [row["geom"]],
                ccrs.PlateCarree(),
                facecolor=COLORS[row["threshold"]],
                edgecolor="k",
                linewidth=2,
                zorder=Z_POLITICAL - 1,
            )
            rect = Rectangle((0, 0), 1, 1, fc=COLORS[row["threshold"]])
        rects.append(rect)
    mp.ax.legend(
        rects,
        df["threshold"].to_list(),
        ncol=1,
        loc="lower right",
        fontsize=12,
        bbox_to_anchor=(1.08, 0.01),
        fancybox=True,
        framealpha=1,
    ).set_zorder(Z_OVERLAY2_LABEL + 100)

    if sector == "cwa":
        mp.draw_cwas()

    for col in ["product_issue", "issue", "expire", "updated"]:
        # some rows could be NaN
        df[col] = df[~pd.isna(df[col])][col].apply(lambda x: x.strftime(ISO))
    return mp.fig, df.drop("geom", axis=1)


if __name__ == "__main__":
    plotter(dict(cat="tornado", valid="2021-03-25 1742"))
