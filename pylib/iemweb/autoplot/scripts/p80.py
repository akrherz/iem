"""
This plot presents the accumulated frequency of duration for a given
NWS VTEC Watch, Warning, Advisory product.  The complication with this
tool is that some alerts are issued for zones and others are for
counties.  If you do not find results for one, try switching to the
other.</p>

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
from pyiem.database import get_dbconn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
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


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    ctx = get_autoplot_context(fdict, get_description())
    ugc = ctx["ugc"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]

    cursor.execute(
        "SELECT s.wfo, s.tzname, u.name from ugcs u  JOIN stations s "
        "on (u.wfo = s.id) where ugc = %s and end_ts is null and "
        "s.network = 'WFO' LIMIT 1",
        (ugc,),
    )
    wfo = None
    name = ""
    if cursor.rowcount == 1:
        row = cursor.fetchone()
        wfo = row[0]
        name = row[2]

    if significance == "A" and phenomena not in ["SV", "TO"]:
        cursor.execute(
            """
        SELECT issue - product_issue, issue - product_issue,
        issue at time zone 'UTC'
        from warnings WHERE ugc = %s and phenomena = %s and significance = %s
        and wfo = %s
        """,
            (ugc, phenomena, significance, wfo),
        )
    else:
        cursor.execute(
            """
        SELECT expire - issue, init_expire - issue, issue at time zone 'UTC'
        from warnings WHERE ugc = %s and phenomena = %s and significance = %s
        and wfo = %s
        """,
            (ugc, phenomena, significance, wfo),
        )
    if cursor.rowcount < 2:
        raise NoDataFound("No Results Found, try flipping zone/county")

    rows = []
    for row in cursor:
        rows.append(  # noqa
            dict(
                final=row[0].total_seconds() / 60.0,
                initial=row[1].total_seconds() / 60.0,
                issue=row[2],
            )
        )

    df = pd.DataFrame(rows)
    title = (
        f"[{ugc}] {name} :: {vtec.get_ps_string(phenomena, significance)} "
        f"({phenomena}.{significance})\n"
        f"Distribution of Event Time Duration {df['issue'].min():%-d %b %Y}"
        f"-{df['issue'].max():%-d %b %Y}"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    titles = {"initial": "Initial Issuance", "final": "Final Duration"}
    for col in ["final", "initial"]:
        sortd = df.sort_values(by=col)
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
    if x[-1] < 120:
        xmax = x[-1] + 10 - (x[-1] % 10)
        ax.set_xlim(0, xmax)
        ax.set_xticks(np.arange(0, xmax + 1, 10))
        ax.set_xlabel("Duration [minutes]")
    else:
        xmax = x[-1] + 60 - (x[-1] % 60)
        ax.set_xlim(0, xmax)
        xticks = np.arange(0, xmax + 1, 60)
        while len(xticks) > 20:
            xticks = xticks[::2]
        ax.set_xticks(xticks)
        ax.set_xticklabels([int(i / 60) for i in xticks])
        ax.set_xlabel("Duration [hours]")
    ax.set_ylabel(f"Frequency [%] out of {y[-1]} Events")

    return fig, df


if __name__ == "__main__":
    plotter({})
