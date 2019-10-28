"""VTEC product duration"""
import psycopg2.extras
import numpy as np
import pandas as pd
import pyiem.nws.vtec as vtec
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot presents the accumulated frequency of
    duration for a given NWS VTEC Watch, Warning, Advisory product."""
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
    """ Go """
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    ugc = ctx["ugc"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    cursor.execute(
        """
    SELECT s.wfo, s.tzname, u.name from ugcs u  JOIN stations s
    on (u.wfo = s.id)
    where ugc = %s and end_ts is null and s.network = 'WFO'
    """,
        (ugc,),
    )
    wfo = None
    name = ""
    if cursor.rowcount == 1:
        row = cursor.fetchone()
        wfo = row[0]
        name = row[2]

    cursor.execute(
        """
     SELECT expire - issue, init_expire - issue, issue at time zone 'UTC'
     from warnings WHERE ugc = %s and phenomena = %s and significance = %s
     and wfo = %s and expire > issue and init_expire > issue
    """,
        (ugc, phenomena, significance, wfo),
    )
    if cursor.rowcount < 2:
        raise NoDataFound("No Results Found, try flipping zone/county")

    rows = []
    for row in cursor:
        rows.append(
            dict(
                final=row[0].total_seconds() / 60.0,
                initial=row[1].total_seconds() / 60.0,
                issue=row[2],
            )
        )

    df = pd.DataFrame(rows)
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
        ax.set_xticks(np.arange(0, xmax + 1, 60))
        ax.set_xticklabels(np.arange(0, (xmax + 1) / 60.0))
        ax.set_xlabel("Duration [hours]")
    ax.set_ylabel("Frequency [%%] out of %s Events" % (y[-1],))
    ax.set_title(
        ("[%s] %s :: %s (%s.%s)\n" "Distribution of Event Time Duration %s-%s")
        % (
            ugc,
            name,
            vtec.get_ps_string(phenomena, significance),
            phenomena,
            significance,
            min(df["issue"]).strftime("%-d %b %Y"),
            max(df["issue"]).strftime("%-d %b %Y"),
        )
    )

    return fig, df


if __name__ == "__main__":
    plotter(dict())
