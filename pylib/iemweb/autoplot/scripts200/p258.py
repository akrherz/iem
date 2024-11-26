"""
This tool generates an info-graphic with the progression of outlooks for a
given point and date.  This plot utilizes the
<a href="/json/outlook_progression.py?help">outlook progression</a> web
service.
"""

from datetime import date

import httpx
import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, utc

from iemweb.autoplot.scripts200.p200 import ISSUANCE
from iemweb.autoplot.scripts200.p220 import COLORS

PDICT = {
    "C": "Convective",
    "E": "Excessive Rainfall",
    "F": "Fire Weather",
}
LABELS = {
    "C": "Storm Prediction Center Convective Outlook",
    "E": "Weather Prediction Center Excessive Rainfall Outlook",
    "F": "Storm Prediction Center Fire Weather Outlook",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    now = utc()
    desc["arguments"] = [
        {
            "type": "date",
            "name": "valid",
            "default": now.strftime("%Y/%m/%d"),
            "label": "Date:",
            "min": "1990/01/01",
        },
        {
            "type": "select",
            "name": "outlook_type",
            "default": "C",
            "label": "Outlook Type:",
            "options": PDICT,
        },
        {
            "type": "float",
            "name": "lat",
            "default": 42.0,
            "label": "Enter Latitude (deg N):",
        },
        {
            "type": "float",
            "name": "lon",
            "default": -95.0,
            "label": "Enter Longitude (deg E):",
        },
    ]
    return desc


def compute_slots(outlook_type: str, valid: date) -> list:
    """Figure out what slots we have"""
    slots = []
    for key in list(ISSUANCE.keys())[::-1]:
        tokens = key.split(".")
        if tokens[1] != outlook_type or tokens[2] == "A":
            continue
        slots.append(key)
    if outlook_type == "C" and valid < date(2024, 8, 22):
        slots.pop(slots.index("3.C.20"))
    return slots


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    jdata = httpx.get(
        "http://iem.local/json/outlook_progression.py",
        params={
            "lat": ctx["lat"],
            "lon": ctx["lon"],
            "valid": ctx["valid"].strftime("%Y-%m-%d"),
            "outlook_type": ctx["outlook_type"],
            "fmt": "json",
        },
    ).json()
    outlooks = pd.DataFrame(jdata["outlooks"])
    if outlooks.empty:
        raise NoDataFound("No outlooks found for this point and date.")

    outlooks["product_issue"] = pd.to_datetime(outlooks["product_issue"])
    fig = figure(
        title=(f"{LABELS[ctx['outlook_type']]} Progression"),
        subtitle=(
            f"Lon: {ctx['lon']:.02f}E Lat: {ctx['lat']:.02f}N for "
            f"{ctx['valid']:%-d %B %Y}"
        ),
    )
    ax = fig.add_axes((0.2, 0.1, 0.75, 0.8))
    y = 0
    xloc = {
        "ANY SEVERE": 1,
        "CATEGORICAL": 2,
        "TORNADO": 3,
        "HAIL": 4,
        "WIND": 5,
    }
    ylabels = []
    ylocator = {}
    slots = compute_slots(fdict["outlook_type"], ctx["valid"])
    for (pissue, cat), df2 in outlooks.groupby(["product_issue", "category"]):
        row0 = df2[df2["threshold"] != "SIGN"].iloc[0]
        if row0["cycle"] != -1:
            # Consume up slots as necessary
            slotkey = f"{row0['day']}.{fdict['outlook_type']}.{row0['cycle']}"
            if slotkey in slots:
                removeme = []
                for index in range(slots.index(slotkey)):
                    slot = slots[index]
                    removeme.append(slot)
                    ylabels.append(
                        f"Day {slot.split('.')[0]}@{slot.split('.')[2]}Z"
                    )
                    y -= 1
                for slot in removeme:
                    slots.pop(slots.index(slot))
            if slots and slotkey == slots[0]:
                slots.pop(0)
        hatched = "SIGN" in df2["threshold"].values
        cycle = row0["cycle"] if row0["cycle"] > -1 else ""
        key = f"Day {row0['day']}@{cycle}Z\nIssued:{pissue:%d/%H%M}Z"
        if key not in ylocator:
            ylocator[key] = y
            y -= 1
            ylabels.append(key)
        if pd.isna(row0["threshold"]):
            continue
        thisy = ylocator[key]
        x = xloc.get(cat, 1)
        color = COLORS.get(row0["threshold"], "tan")
        rect = Rectangle(
            (x - 0.4, thisy - 0.4),
            0.8,
            0.8,
            color=color,
            hatch="/" if hatched else None,
            zorder=3,
        )
        ax.add_patch(rect)
        if hatched:
            ax.add_patch(
                Rectangle(
                    (x - 0.4, thisy - 0.4),
                    0.8,
                    0.8,
                    hatch="//" if hatched else None,
                    fill=False,
                    zorder=4,
                )
            )
        pretty = row0["threshold"]
        if pretty.startswith("0."):
            pretty = f"{int(pretty[2:])}%"
        ax.text(
            x,
            thisy,
            f"{pretty} {cat}",
            ha="center",
            va="center",
            zorder=5,
            color="w",
            bbox=dict(
                facecolor="k",
                alpha=0.7,
                edgecolor="none",
                pad=1,
            ),
        )
    while slots:
        slot = slots.pop(0)
        ylabels.append(f"Day {slot.split('.')[0]}@{slot.split('.')[2]}Z")
        y -= 1

    ax.set_yticks(range(-len(ylabels) + 1, 1))
    ax.set_yticklabels(ylabels[::-1])
    ax.set_ylim(-len(ylabels), 0.6)
    ax.set_xlim(0.5, 5.5)
    ax.set_xticks([])
    # Only show y-axis grid
    ax.grid(axis="y")
    return fig, outlooks
