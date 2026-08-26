"""
This chart presents a monthly average number of VTEC advisory/warnings. Since
these alerts can be issued for either counties, forecast zones, marine zones,
or fire weather zones, the user can select one or up to three different NWS
UGC codes to use for the computed statistics.  Note
also that while some warnings are polygon based, this autoplot does bean
counting at the UGC level.
</p>

<p>
The main trickiness of this autoplot is the event counts.  You can either count
an individual warning/advisory as a single event, no matter how many UGCs it
covers <strong>or</strong> count each UGC covered by a warning/advisory as a
separate event.
</p>

<p>
For the initial implementation of this chart, watches are excluded as it is not
yet clear how best to handle these.
</p>
"""

import calendar
from datetime import date

import numpy as np
import pandas as pd
from pyiem import reference
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.autoplot import ARG_FEMA, fema_region2states

AVG_YEAR1 = 2008
LAST_YEAR = date.today().year
PDICT = {
    "wfo": "Select by NWS Forecast Office",
    "state": "Select by State",
    "ugc": "Select by NWS County/Forecast Zone",
    "fema": "Select by FEMA Region",
}
PDICT2 = {
    "per_eventid": "Count by Event ID",
    "per_ugc": "Count by UGCs Covered",
}
PHENOM_CONFIG = {
    "Winter Weather": {
        "color": "blue",
        "phenoms": ["WW", "WS", "BZ"],
    },
    "Frost/Freeze": {
        "color": "lightblue",
        "phenoms": ["FZ", "FR"],
    },
    "Severe Thunderstorm": {
        "color": "orange",
        "phenoms": ["SV"],
    },
    "Tornado": {
        "color": "red",
        "phenoms": ["TO"],
    },
    "Severe Cold": {
        "color": "cyan",
        "phenoms": ["WC", "EC"],
    },
    "Dense Fog": {
        "color": "#000000cc",
        "phenoms": ["FG"],
    },
    "Flood": {
        "color": "lightgreen",
        "phenoms": ["FF", "FA", "FL"],
    },
    "Marine": {
        "color": "darkgreen",
        "phenoms": ["MA", "SC", "GL", "CF"],
    },
    "Tropical": {
        "color": "darkred",
        "phenoms": ["TR", "HU", "TS"],
    },
    "High Heat": {
        "color": "purple",
        "phenoms": ["HT", "XH", "EH"],
    },
    "Fire Weather": {
        "color": "darkorange",
        "phenoms": [
            "FW",
        ],
    },
    "Wind": {
        "color": "darkgray",
        "phenoms": ["WI", "HW"],
    },
    "Other": {
        "color": "gray",
        "phenoms": [],
    },
}


def get_description():
    """Return a dict describing how to call this plotter"""
    doc = __doc__ + "<p>VTEC Codes used for each category are:</p><ul>"
    for name, config in PHENOM_CONFIG.items():
        if name == "Other":
            continue
        doc += f"<li>{name}: {', '.join(config['phenoms'])}</li>"
    doc += "</ul>"
    desc = {"description": doc, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="select",
            name="opt",
            default="ugc",
            options=PDICT,
            label="How to summarize the data?",
        ),
        {
            "type": "select",
            "name": "how",
            "default": "per_ugc",
            "label": "How is an event counted?",
            "options": PDICT2,
        },
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
        ),
        dict(type="state", name="state", default="IA", label="Select State:"),
        ARG_FEMA,
        {
            "type": "ugc",
            "name": "ugc",
            "default": "IAC169",
            "label": "Select UGC Zone/County:",
        },
        {
            "optional": True,
            "type": "ugc",
            "name": "ugc2",
            "default": "IAC169",
            "label": "Select Second Additional UGC Zone/County: (optional)",
        },
        {
            "optional": True,
            "type": "ugc",
            "name": "ugc3",
            "default": "IAC169",
            "label": "Select Third Additional UGC Zone/County: (optional)",
        },
    ]
    return desc


def get_ugc_name(ugc):
    """Return the WFO and county name."""
    cursor = get_dbconn("postgis").cursor()
    cursor.execute(
        "SELECT name, wfo from ugcs where ugc = %s and end_ts is null", (ugc,)
    )
    return cursor.fetchone()


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    opt = ctx["opt"]
    state = ctx["state"]
    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }

    params = {
        "tzname": ctx["_nt"].sts[station]["tzname"],
        "first_year": AVG_YEAR1,
    }
    wfo_limiter = " and wfo = :wfo "
    params["wfo"] = station if len(station) == 3 else station[1:]
    if opt == "state":
        wfo_limiter = " and substr(ugc, 1, 2) = :state "
        params["state"] = state
    elif opt == "fema":
        wfo_limiter = " and substr(ugc, 1, 2) = ANY(:states) "
        params["states"] = fema_region2states(ctx["fema"])
    elif opt == "ugc":
        wfo_limiter = " and ugc = ANY(:ugcs) "
        params["ugcs"] = [
            ctx["ugc"],
        ]
        if (ugc2 := ctx.get("ugc2")) is not None:
            params["ugcs"].append(ugc2)
        if (ugc3 := ctx.get("ugc3")) is not None:
            params["ugcs"].append(ugc3)

    with get_sqlalchemy_conn("postgis") as conn:
        # vtec_year is likely "good enough" for this, eventid is 99.99% of the
        # time OK and not repeated.  We are dealing with agg stats for this.
        eventsdf = pd.read_sql(
            sql_helper(
                """
                SELECT
                distinct vtec_year, wfo, {eagg}
                phenomena, significance, eventid,
                extract(month from issue at time zone :tzname) as month
                from warnings where significance in ('W', 'Y') and
                vtec_year >= :first_year
                {wfo_limiter}
                ORDER by vtec_year asc, month asc
        """,
                wfo_limiter=wfo_limiter,
                eagg="" if ctx["how"] == "per_eventid" else "ugc,",
            ),
            conn,
            params=params,
            index_col=None,
        )

    if eventsdf.empty:
        raise NoDataFound("Database query found no entries!")

    # Assign categories
    for name, config in PHENOM_CONFIG.items():
        if name == "Other":
            continue
        eventsdf.loc[
            eventsdf["phenomena"].isin(config["phenoms"]), "category"
        ] = name
    # Everything else is Other
    eventsdf["category"] = eventsdf["category"].fillna("Other")

    title = f"NWS {ctx['_sname']}"
    subtitle = PDICT2[ctx["how"]]
    if opt == "state":
        title = (
            "NWS Issued for Counties/Zones for State of "
            f"{reference.state_names[state]}"
        )
    elif opt == "ugc":
        title = "NWS Issued Warnings/Advisories by Month"
        parts = []
        for suffix in ["", "1", "2"]:
            if (ugc := ctx.get(f"ugc{suffix}")) is not None:
                name, _wfo = get_ugc_name(ugc)
                parts.append(f"[{ugc}] {name}")
        subtitle += f" For UGC: {'; '.join(parts)}"
    elif opt == "fema":
        title = f"NWS Issued for FEMA Region {ctx['fema']}"
    (fig, ax) = figure_axes(
        title=f"[{AVG_YEAR1}-{LAST_YEAR}] {title}",
        subtitle=subtitle,
        apctx=ctx,
    )
    for spine in ["right", "top", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.set_position((0.2, 0.5, 0.75, 0.4))
    years = LAST_YEAR - AVG_YEAR1 + 1
    bar_bottom = np.zeros(12)
    celltext = []
    row_labels = []
    for category in PHENOM_CONFIG:
        df2 = eventsdf[eventsdf["category"] == category]
        if df2.empty:
            continue
        df2 = (
            df2.groupby("month")
            .count()[["vtec_year"]]
            .rename(columns={"vtec_year": "count"})
            .reindex(range(1, 13), fill_value=0)
        )
        df2["count"] = df2["count"] / years
        ax.bar(
            df2.index.values,
            df2["count"].values,
            bottom=bar_bottom,
            color=PHENOM_CONFIG.get(category, {}).get("color", None),
        )
        row_labels.append(category)
        celltext.append([f"{x:0.1f}" for x in df2["count"].values.tolist()])
        bar_bottom = bar_bottom + df2["count"].values

    row_labels.append("Total")
    celltext.append([f"{x:0.1f}" for x in bar_bottom])

    ax.set_xlim(0.5, 12.5)
    ax.set_xticks([])
    ax.set_ylabel("Average Number of Events per Year")

    # Make the pretty table now
    num_rows = len(row_labels) + 1
    table_height = 0.06 * num_rows
    row_colors = [
        PHENOM_CONFIG.get(cat, {}).get("color", "white") for cat in row_labels
    ]
    table = ax.table(
        cellText=celltext,
        colLabels=calendar.month_abbr[1:],
        rowLabels=row_labels,
        rowColours=row_colors,
        loc="bottom",
        bbox=[0, -table_height, 1, table_height],
    )
    for (r, c), cell in table.get_celld().items():
        if c == -1 and r > 0:
            fc = cell.get_facecolor()
            lum = 0.2126 * fc[0] + 0.7152 * fc[1] + 0.0722 * fc[2]
            if lum < 0.5:
                cell.get_text().set_color("white")

    return fig, eventsdf
