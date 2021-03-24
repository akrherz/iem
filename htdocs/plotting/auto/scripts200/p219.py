"""Visualization of TAFs"""
import datetime

# third party
import requests
import pandas as pd
import numpy as np
import matplotlib.patheffects as PathEffects
from matplotlib.patches import Rectangle
from metpy.units import units
from metpy.calc import wind_components
from pandas.io.sql import read_sql
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_dbconn, utc
from pyiem.exceptions import NoDataFound

TEXTARGS = {
    "fontsize": 12,
    "color": "k",
    "ha": "center",
    "va": "center",
    "zorder": 3,
}
PE = [PathEffects.withStroke(linewidth=3, foreground="white")]


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 600
    desc[
        "description"
    ] = """
    This app generates infographics for Terminal Aerodome Forecasts (TAF).
    You need not provide an exact valid timestamp for the TAF issuance, the
    app will search backwards in time up to 24 hours to find the nearest
    issuance stored in the database.
    """
    desc["arguments"] = [
        dict(
            type="text",
            default="KDSM",
            name="station",
            label="Select station to plot:",
        ),
        dict(
            type="datetime",
            name="valid",
            default=utc().strftime("%Y/%m/%d %H%M"),
            label="TAF Issuance/Valid Timestamp (UTC Timezone):",
            min="1995/01/01 0000",
        ),
    ]
    return desc


def get_text(product_id):
    """get the raw text."""
    text = "Text Unavailable, Sorry."
    uri = f"https://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}"
    try:
        req = requests.get(uri, timeout=5)
        if req.status_code == 200:
            text = req.content.decode("ascii", "ignore").replace("\001", "")
            text = "\n".join(text.replace("\r", "").split("\n")[5:])
    except Exception:
        pass

    return text


def taf_search(pgconn, station, valid):
    """Go look for a nearest in time TAF."""
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT valid at time zone 'UTC' from taf "
        "WHERE station = %s and valid > %s and "
        "valid < %s ORDER by valid DESC",
        (station, valid - datetime.timedelta(hours=24), valid),
    )
    if cursor.rowcount == 0:
        return None
    return cursor.fetchone()[0].replace(tzinfo=datetime.timezone.utc)


def compute_flight_condition(row):
    """What's our status."""
    if row["visibility"] >= 5:
        return "VFR"
    level = 10000
    if "OVC" in row["skyc"]:
        level = row["skyl"][row["skyc"].index("OVC")]
    if level < 500 or row["visibility"] < 1:
        return "LIFR"
    if level < 1000 or row["visibility"] < 3:
        return "IFR"
    if level < 3000 or row["visibility"] < 5:
        return "MVFR"
    return "UNK"


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    valid = ctx["valid"].replace(tzinfo=datetime.timezone.utc)
    pgconn = get_dbconn("asos")

    def fetch(ts):
        """Getme data."""
        return read_sql(
            "SELECT f.*, t.product_id from taf t JOIN taf_forecast f on "
            "(t.id = f.taf_id) WHERE t.station = %s and t.valid = %s "
            "ORDER by f.valid ASC",
            pgconn,
            params=(ctx["station"], ts),
            index_col="valid",
        )

    df = fetch(valid)
    if df.empty:
        valid = taf_search(pgconn, ctx["station"], valid)
        if valid is None:
            raise NoDataFound("TAF data was not found!")
        df = fetch(valid)
    df = df.fillna(np.nan)
    product_id = df.iloc[0]["product_id"]
    title = (
        f"{ctx['station']} Terminal Aerodome Forecast by NWS "
        f"{product_id[14:17]}\n"
        f"Valid: {valid.strftime('%-d %b %Y %H:%M UTC')}"
    )
    fig = figure(title=title)

    ###
    text = get_text(product_id)
    res = fig.text(0.5, 0.01, text.strip(), va="bottom", fontsize=12)
    bbox = res.get_window_extent(fig.canvas.get_renderer())
    figbbox = fig.get_window_extent()
    yndc = bbox.y1 / figbbox.y1

    # Create the main axes that will hold all our hackery
    ax = fig.add_axes([0.08, yndc + 0.05, 0.9, 0.9 - yndc - 0.05])
    fig.text(0.015, 0.3, "Cloud Coverage & Level", rotation=90)

    df["u"], df["v"] = wind_components(
        units("knot") * df["sknt"].values,
        units("degree") * df["drct"].values,
    )
    df["ws_u"], df["ws_v"] = wind_components(
        units("knot") * df["ws_sknt"].values,
        units("degree") * df["ws_drct"].values,
    )
    sz = len(df.index)
    clevels = []
    for valid, row in df.iterrows():
        # Between 1-3 plot the clouds
        for j, skyc in enumerate(row["skyc"]):
            level = min([3200, row["skyl"][j]]) / 1600 + 1
            if j + 1 == len(row["skyc"]):
                clevels.append(level)
            ax.text(valid, level, skyc, **TEXTARGS).set_path_effects(PE)

        # At 0.9 present weather
        ax.text(
            valid, 0.9, " ".join(row["presentwx"]), **TEXTARGS
        ).set_path_effects(PE)
        # Plot wind as text string
        if not pd.isna(row["ws_sknt"]):
            ax.text(
                valid,
                4 + (0.25 if row["v"] > 0 else -0.25),
                "WS%g" % (row["ws_sknt"],),
                ha="center",
                fontsize=TEXTARGS["fontsize"],
                va="top" if row["v"] < 0 else "bottom",
                color="r",
            ).set_path_effects(PE)
        text = f"{row['sknt']:.0f}"
        if not pd.isna(row["gust"]) and row["gust"] > 0:
            text += f"G{row['gust']:.0f}"
        if not pd.isna(row["sknt"]):
            ax.text(
                valid,
                4 + (0.1 if row["v"] > 0 else -0.1),
                f"{text}",
                ha="center",
                fontsize=TEXTARGS["fontsize"],
                color=TEXTARGS["color"],
                va="top" if row["v"] < 0 else "bottom",
            ).set_path_effects(PE)

        df.at[valid, "fcond"] = compute_flight_condition(row)
        # At 3.25 plot the visibility
        ax.text(
            valid, 3.25, f"{row['visibility']:g}", **TEXTARGS
        ).set_path_effects(PE)

    if clevels:
        ax.plot(df.index.values, clevels, linestyle=":", zorder=2)

    # Between 3.5-4.5 plot the wind arrows
    ax.barbs(
        df.index.values,
        [4] * sz,
        df["u"].values,
        df["v"].values,
        zorder=3,
        color="k",
    )
    ax.barbs(
        df.index.values,
        [4] * sz,
        df["ws_u"].values,
        df["ws_v"].values,
        zorder=4,
        color="r",
    )

    padding = datetime.timedelta(minutes=60)
    ax.set_xlim(df.index.min() - padding, df.index.max() + padding)
    ax.set_yticks([0.9, 1.5, 2, 2.5, 3, 3.25, 4])
    ax.set_yticklabels(
        [
            "WX",
            "800ft",
            "1600ft",
            "2400ft",
            "3200+ft",
            "Vis (mile)",
            "Wind (KT)",
        ]
    )
    ax.set_ylim(0.8, 4.5)
    for y in [1, 3.125, 3.375]:
        ax.axhline(
            y,
            color="blue",
            lw=0.5,
        )

    colors = {
        "UNK": "#EEEEEE",
        "VFR": "green",
        "MVFR": "blue",
        "IFR": "red",
        "LIFR": "magenta",
    }
    # Colorize things by flight condition
    xs = df.index.to_list()
    xs[0] = xs[0] - padding
    xs.append(df.index.max() + padding)
    for i, val in enumerate(df["fcond"].values):
        ax.axvspan(
            xs[i],
            xs[i + 1],
            fc=colors.get(val, "white"),
            ec="None",
            alpha=0.5,
            zorder=2,
        )
    rects = []
    for fcond in colors:
        rects.append(Rectangle((0, 0), 1, 1, fc=colors[fcond], alpha=0.5))
    ax.legend(
        rects,
        colors.keys(),
        ncol=3,
        loc="upper left",
        fontsize=14,
        bbox_to_anchor=(0.0, -0.04),
        fancybox=True,
        shadow=True,
    )

    return fig, df


if __name__ == "__main__":
    plotter(dict(station="KOLM", valid="2021-03-23 1720"))
