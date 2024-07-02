"""
This plot presents the accumulated frequency of duration for a given
NWS VTEC Watch, Warning, Advisory product.  The complication with this
tool is that some alerts are issued for zones and others are for
counties.  If you do not find results for one, try switching to the
other.</p>

<p>When you plot by a WFO, this tool will treat each individual combination
of a VTEC event and UGC has an individual event.</p>

<p>There's a second major complication and that is the case of watches
and how VTEC handles issuance and expiration time.  Some watches are
issued for time periods well into the future and are either cancelled
or upgraded prior to the VTEC issuance time.  In those cases, this app
considers the wall clock issuance time of the watch as the start time
and the wall clock time when the watch was either cancelled or upgraded.
In this case, both lines are presented as equal.
"""

import numpy as np
import pandas as pd
import pyiem.nws.vtec as vtec
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from sqlalchemy import text

from iemweb.autoplot import get_monofont

PDICT = {
    "wfo": "Summarize by NWS Forecast Office",
    "ugc": "Summarize by UGC Zone/County",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        {
            "type": "select",
            "name": "which",
            "default": "ugc",
            "label": "Summarize By:",
            "options": PDICT,
        },
        {
            "type": "networkselect",
            "name": "wfo",
            "default": "DMX",
            "network": "WFO",
            "label": "Select NWS Forecast Office:",
        },
        dict(
            type="ugc",
            name="ugc",
            default="IAC153",
            label="Select UGC Zone/County:",
        ),
        dict(
            type="phenomena",
            name="phenomena",
            default="TO",
            label="Select Watch/Warning Phenomena Type:",
        ),
        dict(
            type="significance",
            name="significance",
            default="A",
            label="Select Watch/Warning Significance Level:",
        ),
    ]
    return desc


def print_top(fig, events: pd.DataFrame):
    """Add some bling."""
    x = 0.77
    y = 0.85
    font = get_monofont()
    uts = "Mins"
    if events["max"].max() > 120:
        uts = "Hours"
    for typ, bpoint in zip(["Longest", "Shortest"], [0.5, 0.1]):
        fig.text(
            x,
            y,
            f"Date[ETN]: {typ} ({uts})",
            ha="left",
            fontproperties=font,
        )
        done = []
        asc = typ == "Shortest"
        col = "max" if typ == "Longest" else "min"
        for row in events.sort_values(by=col, ascending=asc).itertuples():
            key = f"{row.year}_{row.eventid}"
            if key in done:
                continue
            done.append(key)
            y -= 0.035
            val = getattr(row, col)
            lbl = f"{val:.0f}" if uts == "Mins" else f"{val / 60:.1f}"
            fig.text(
                x,
                y,
                f"{row.issue:%Y-%m-%d}[{row.eventid:4.0f}]: {lbl}",
                ha="left",
                fontproperties=font,
            )
            if y < bpoint:
                break
        y -= 0.05


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ugc = ctx["ugc"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    params = {
        "phenomena": phenomena,
        "significance": significance,
        "wfo": ctx["wfo"],
        "ugc": ugc,
        "tzname": "America/Chicago",
    }
    lid = ugc
    name = ""
    ugclimiter = ""
    if ctx["which"] == "ugc":
        with get_sqlalchemy_conn("postgis") as conn:
            res = conn.execute(
                text("""
                    SELECT s.wfo, s.tzname, u.name from ugcs u JOIN stations s
                    on (u.wfo = s.id) where ugc = :ugc and end_ts is null and
                    s.network = 'WFO' LIMIT 1
                     """),
                params,
            )
            if res.rowcount == 1:
                row = res.fetchone()
                params["wfo"] = row[0]
                params["tzname"] = row[1]
                name = row[2]
        ugclimiter = " ugc = :ugc and "
    else:
        lid = f"NWS {ctx['wfo']}"
        name = ctx["_nt"].sts[ctx["wfo"]]["name"]
        params["tzname"] = ctx["_nt"].sts[ctx["wfo"]]["tzname"]

    issuecol = "issue"
    expirecol = "expire"
    expirecol2 = "init_expire"
    if significance == "A" and phenomena not in ["SV", "TO"]:
        issuecol = "product_issue"
        expirecol = "issue"
        expirecol2 = "issue"

    with get_sqlalchemy_conn("postgis") as conn:
        events = pd.read_sql(
            text(f"""
                SELECT {expirecol} - {issuecol} as final,
                {expirecol2} - {issuecol} as initial,
                issue at time zone :tzname as issue, ugc, eventid,
                vtec_year as year
                from warnings WHERE {ugclimiter} phenomena = :phenomena
                and significance = :significance and wfo = :wfo
                 """),
            conn,
            params=params,
        )
    if len(events.index) < 2:
        raise NoDataFound("No Results Found, try flipping zone/county")
    for col in ["final", "initial"]:
        events[col] = events[col].dt.total_seconds() / 60.0
    events["max"] = events[["final", "initial"]].max(axis=1)
    events["min"] = events[["final", "initial"]].min(axis=1)

    title = (
        f"[{lid}] {name} :: {vtec.get_ps_string(phenomena, significance)} "
        f"({phenomena}.{significance})\n"
        "Distribution of Event Time Duration "
        f"{events['issue'].min():%-d %b %Y}-{events['issue'].max():%-d %b %Y}"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.set_position([0.1, 0.1, 0.65, 0.8])
    print_top(fig, events)

    titles = {"initial": "Initial Issuance", "final": "Final Duration"}
    for col in ["final", "initial"]:
        sortd = events.sort_values(by=col)
        x = []
        y = []
        i = 0
        for _, row in sortd.iterrows():
            i += 1
            if i == 1:
                x.append(row[col])
                y.append(i)
                continue
            if x[-1] == row[col]:
                y[-1] = i
                continue
            y.append(i)
            x.append(row[col])

        ax.plot(x, np.array(y) / float(y[-1]) * 100.0, lw=2, label=titles[col])
    ax.grid()
    ax.legend(loc=2, ncol=2, fontsize=12)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    xmax = events["max"].max()
    if xmax < 120:
        xmax = xmax + 10 - (xmax % 10)
        ax.set_xlim(0, xmax)
        ax.set_xticks(np.arange(0, xmax + 1, 10))
        ax.set_xlabel("Duration [minutes]")
    else:
        xmax = xmax + 60 - (xmax % 60)
        ax.set_xlim(0, xmax)
        xticks = np.arange(0, xmax + 1, 60)
        while len(xticks) > 20:
            xticks = xticks[::2]
        ax.set_xticks(xticks)
        ax.set_xticklabels([int(i / 60) for i in xticks])
        ax.set_xlabel("Duration [hours]")
    ax.set_ylabel(f"Frequency [%] out of {y[-1]} Events")

    return fig, events.drop(columns=["max", "min"])
