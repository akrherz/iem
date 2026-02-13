"""
This app generates infographics for Terminal Aerodome Forecasts (TAF).
You need not provide an exact valid timestamp for the TAF issuance, the
app will search backwards in time up to 24 hours to find the nearest
issuance stored in the database.
"""

import time
from datetime import datetime, timedelta, timezone

import httpx
import matplotlib.patheffects as PathEffects
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from metpy.calc import wind_components
from metpy.units import units
from pyiem.database import (
    get_dbconn,
    get_sqlalchemy_conn,
    sql_helper,
    with_sqlalchemy_conn,
)
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import LOG, utc
from sqlalchemy.engine import Connection

VIS = "visibility"
TEXTARGS = {
    "fontsize": 12,
    "color": "k",
    "ha": "center",
    "va": "center",
    "zorder": 3,
}
PE = [PathEffects.withStroke(linewidth=5, foreground="white")]


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["defaults"] = {"_r": "t"}
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
    # Allow for some time for the product to show up in AFOS
    for attempt in range(2):
        try:
            resp = httpx.get(uri, timeout=5)
            resp.raise_for_status()
            text = resp.content.decode("ascii", "ignore").replace("\001", "")
            text = "\n".join(text.replace("\r", "").split("\n")[5:])
            break
        except Exception as exp:
            if attempt > 0:
                LOG.warning(exp)
            time.sleep(10)

    return text


@with_sqlalchemy_conn("asos")
def taf_search(station, valid, conn: Connection | None = None):
    """Go look for a nearest in time TAF."""
    res = conn.execute(
        sql_helper(
            "SELECT valid at time zone 'UTC' from taf "
            "WHERE station = :station and valid > :sts and "
            "valid <= :ets ORDER by valid DESC"
        ),
        {"station": station, "sts": valid - timedelta(hours=24), "ets": valid},
    )
    if res.rowcount == 0:
        return None
    return res.fetchone()[0].replace(tzinfo=timezone.utc)


def compute_flight_condition(row):
    """What's our status."""
    # TEMPO may not address sky or vis
    if row["ftype"] == 2 and (not row["skyc"] or pd.isna(row[VIS])):
        return None
    level = 10000
    if "SKC" in row["skyc"]:
        return "VFR"
    if "OVC" in row["skyc"]:
        level = row["skyl"][row["skyc"].index("OVC")]
    if level == 10000 and "BKN" in row["skyc"]:
        level = row["skyl"][row["skyc"].index("BKN")]
    if row[VIS] > 5 and level > 3000:
        return "VFR"
    if level < 500 or row[VIS] < 1:
        return "LIFR"
    if level < 1000 or row[VIS] < 3:
        return "IFR"
    if level <= 3000 or row[VIS] <= 5:
        return "MVFR"
    return "UNK"


def fetch(station: str, ts: datetime) -> pd.DataFrame:
    """Getme data."""
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            sql_helper("""
    SELECT f.*, t.product_id,
    coalesce(t.is_amendment, false) as is_amendment
    from taf t JOIN taf_forecast f on
    (t.id = f.taf_id) WHERE t.station = :station and t.valid = :valid
    and ftype in (0, 1, 2)
    ORDER by f.valid ASC"""),
            conn,
            params={"station": station, "valid": ts},
            index_col="valid",
        )
    return df


def plotter(ctx: dict):
    """Go"""
    valid = ctx["valid"].replace(tzinfo=timezone.utc)
    df = fetch(ctx["station"], valid)
    if df.empty:
        pgconn = get_dbconn("asos")
        valid = taf_search(ctx["station"], valid)
        pgconn.close()
        if valid is None:
            raise NoDataFound("TAF data was not found!")
        df = fetch(ctx["station"], valid)
    # prevent all nan from becoming an object
    df = df.fillna(np.nan).infer_objects()
    df["next_valid"] = (
        df.reset_index().shift(-1)["valid"].values - df.index.values
    )
    product_id = df.iloc[0]["product_id"]
    amd = "Amended " if df.iloc[0]["is_amendment"] else ""
    title = (
        f"{ctx['station']} {amd}Terminal Aerodome Forecast by NWS "
        f"{product_id[14:17]}\n"
        f"Valid: {valid.strftime('%-d %b %Y %H:%M UTC')}"
    )
    text = get_text(product_id)
    if len(text.split("\n")) > 10:
        raise NoDataFound(f"TAF text {product_id} is too long to plot!")
    fig = figure(title=title, apctx=ctx)

    ###
    res = fig.text(0.43, 0.01, text.strip(), va="bottom", fontsize=12)
    bbox = res.get_window_extent(fig.canvas.get_renderer())
    figbbox = fig.get_window_extent()
    # one-two line TAFs cause the legend to go off-screen
    yndc = max([bbox.y1 / figbbox.y1, 0.13])
    # Create the main axes that will hold all our hackery
    ax = fig.add_axes((0.08, yndc + 0.05, 0.9, 0.9 - yndc - 0.05))
    fig.text(0.015, 0.3, "Cloud Coverage & Level", rotation=90)

    df["u"], df["v"] = [
        x.m
        for x in wind_components(
            units("knot") * df["sknt"].values,
            units("degree") * df["drct"].values,
        )
    ]
    df["ws_u"], df["ws_v"] = [
        x.m
        for x in wind_components(
            units("knot") * df["ws_sknt"].values,
            units("degree") * df["ws_drct"].values,
        )
    ]
    # Initialize a fcond with string type
    df["fcond"] = ""
    sz = len(df.index)
    clevels = []
    clevelx = []
    for valid0, row in df.iterrows():
        valid = valid0
        if not pd.isna(row["end_valid"]):
            valid = valid + (row["end_valid"] - valid) / 2
        # Between 1-3 plot the clouds
        for j, skyc in enumerate(row["skyc"]):
            level = 3
            if skyc != "SKC":
                level = min([3200, row["skyl"][j]]) / 1600 + 1
                if j + 1 == len(row["skyc"]):
                    clevelx.append(valid)
                    clevels.append(level)
            ax.text(valid, level, skyc, **TEXTARGS).set_path_effects(PE)

        # At 0.9 present weather
        delta = row["next_valid"]
        rotation = 0
        if not pd.isna(delta) and delta < timedelta(hours=2):
            rotation = 45
        ax.text(
            valid,
            0.9,
            "\n".join(row["presentwx"]),
            rotation=rotation,
            **TEXTARGS,
        ).set_path_effects(PE)
        # Plot wind as text string
        if pd.notna(row["ws_sknt"]):
            ax.text(
                valid,
                3.8 + 0.5,
                f"WS{row['ws_sknt']:.0f}",
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
                3.8 + 0.35,
                f"{text}KT",
                ha="center",
                fontsize=TEXTARGS["fontsize"],
                color=TEXTARGS["color"],
                va="top" if row["v"] < 0 else "bottom",
            ).set_path_effects(PE)
        df.at[valid0, "fcond"] = compute_flight_condition(row)
        # At 3.25 plot the visibility
        if not pd.isna(row[VIS]):
            pltval = f"{row['visibility']:g}"
            if row["visibility"] > 6:
                pltval = "6+"
            ax.text(valid, 3.25, pltval, **TEXTARGS).set_path_effects(PE)

    if clevels:
        ax.plot(clevelx, clevels, linestyle=":", zorder=2)

    # Between 3.5-4.5 plot the wind arrows
    ax.barbs(
        df.index.values,
        [3.8] * sz,
        df["u"].values,
        df["v"].values,
        zorder=3,
        color="k",
    )
    ax.barbs(
        df.index.values,
        [3.8] * sz,
        df["ws_u"].values,
        df["ws_v"].values,
        zorder=4,
        color="r",
    )

    padding = timedelta(minutes=60)
    ax.set_xlim(df.index.min() - padding, df.index.max() + padding)
    ax.set_yticks([0.9, 1.5, 2, 2.5, 3, 3.25, 3.8])
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
    previous = "VFR"
    for i, val_in in enumerate(df["fcond"].values):
        val = previous if val_in is None else val_in
        previous = val
        ax.axvspan(
            xs[i],
            xs[i + 1],
            fc=colors.get(val, "white"),
            ec="None",
            alpha=0.5,
            zorder=2,
        )
    rects = [
        Rectangle((0, 0), 1, 1, fc=item, alpha=0.5) for item in colors.values()
    ]
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

    # Need to get rid of timezones
    df = df.reset_index()
    for col in ["valid", "end_valid"]:
        # some rows could be NaN
        df[col] = df[pd.notna(df[col])][col].apply(
            lambda x: x.strftime("%Y-%m-%d %H:%M")
        )
    return fig, df.drop("next_valid", axis=1)
