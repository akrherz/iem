"""VTEC frequency"""
import datetime

import numpy as np
import pandas as pd
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
import pyiem.nws.vtec as vtec
from pyiem.exceptions import NoDataFound


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 3600
    desc[
        "description"
    ] = """This chart displays the relative frequency of
    VTEC products.  This is computed by taking the unique combination of
    events and UGC county/zones.  Restating and for example, a single
    Severe Thunderstorm Warning covering portions of two counties would
    count as two events in this summary. The values plotted are relative to the
    most frequent product."""
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
            all=True,
        ),
        dict(
            type="year",
            name="syear",
            default=2009,
            label="Start Year (inclusive):",
            min=2009,
        ),
        dict(
            type="year",
            name="eyear",
            default=datetime.date.today().year,
            label="End Year (inclusive):",
            min=2009,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("postgis")
    pcursor = pgconn.cursor()
    ctx = get_autoplot_context(fdict, get_description())
    ctx["_nt"].sts["_ALL"] = dict(name="ALL WFOs")
    syear = ctx["syear"]
    eyear = ctx["eyear"] + 1
    station = ctx["station"][:4]
    sts = datetime.date(syear, 1, 1)
    ets = datetime.date(eyear, 1, 1)
    wfo_limiter = " and wfo = '%s' " % (
        station if len(station) == 3 else station[1:],
    )
    if station == "_ALL":
        wfo_limiter = ""

    pcursor.execute(
        f"""
        select phenomena, significance, min(issue), count(*) from warnings
        where ugc is not null and issue > %s
        and issue < %s {wfo_limiter}
        GROUP by phenomena, significance ORDER by count DESC
    """,
        (sts, ets),
    )
    if pcursor.rowcount == 0:
        raise NoDataFound("No data found.")
    labels = []
    vals = []
    cnt = 1
    rows = []
    for row in pcursor:
        label = ("%s. %s (%s.%s)") % (
            cnt,
            vtec.get_ps_string(row[0], row[1]),
            row[0],
            row[1],
        )
        if cnt < 26:
            labels.append(label)
            vals.append(row[3])
        rows.append(
            dict(
                phenomena=row[0],
                significance=row[1],
                count=row[3],
                wfo=station,
            )
        )
        cnt += 1
    df = pd.DataFrame(rows)
    (fig, ax) = plt.subplots(1, 1, figsize=(7, 10))
    vals = np.array(vals)

    ax.barh(
        np.arange(len(vals)), vals / float(vals[0]) * 100.0, align="center"
    )
    for i in range(1, len(vals)):
        y = vals[i] / float(vals[0]) * 100.0
        ax.text(y + 1, i, "%.1f%%" % (y,), va="center")
    fig.text(
        0.5,
        0.95,
        "%s-%s NWS %s Watch/Warning/Advisory Totals"
        % (
            syear,
            eyear - 1 if (eyear - 1 != syear) else "",
            ctx["_nt"].sts[station]["name"],
        ),
        ha="center",
    )
    fig.text(
        0.5,
        0.05,
        "Event+County/Zone Count, Relative to #%s" % (labels[0],),
        ha="center",
        fontsize=10,
    )
    ax.set_ylim(len(vals), -0.5)
    ax.grid(True)
    ax.set_yticklabels(labels)
    ax.set_yticks(np.arange(len(vals)))
    ax.set_position([0.5, 0.1, 0.45, 0.83])
    ax.set_xticks([0, 10, 25, 50, 75, 90, 100])

    return fig, df


if __name__ == "__main__":
    plotter(dict())
