"""
For a given watch/warning/advisory type and forecast
zone, what is the frequency by time of day that the product was valid.  The
total number of events for the county/zone is used for the frequency. Due
to how the NWS issues some products for counties and some products for
zones, you may need to try twice to get the proper one selected.

<p><a href="/plotting/auto/?q=72">Autoplot 72</a> is similar to this, but
plots for a single WFO at a time.
"""

import numpy as np
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot import figure_axes
from sqlalchemy.engine import Connection


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="ugc",
            name="ugc",
            default="IAZ048",
            label="Select UGC Zone/County:",
        ),
        dict(
            type="phenomena",
            name="phenomena",
            default="WC",
            label="Select Watch/Warning Phenomena Type:",
        ),
        dict(
            type="significance",
            name="significance",
            default="W",
            label="Select Watch/Warning Significance Level:",
        ),
    ]
    return desc


@with_sqlalchemy_conn("postgis")
def plotter(ctx: dict, conn: Connection):
    """Go"""
    ugc = ctx["ugc"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]

    res = conn.execute(
        sql_helper("""
    SELECT s.wfo, s.tzname, u.name from ugcs u JOIN stations s on
    (u.wfo = s.id) where ugc = :ugc and end_ts is null and
    s.network = 'WFO' LIMIT 1"""),
        {"ugc": ugc},
    )
    wfo = None
    tzname = None
    name = ""
    if res.rowcount == 1:
        row = res.fetchone()
        tzname = row[1]
        wfo = row[0]
        name = row[2]
    params = {
        "tzname": tzname,
        "ugc": ugc,
        "phenomena": phenomena,
        "significance": significance,
        "wfo": wfo,
    }
    res = conn.execute(
        sql_helper("""
    SELECT count(*), min(issue at time zone :tzname),
    max(issue at time zone :tzname)
    from warnings WHERE ugc = :ugc and phenomena = :phenomena
    and significance = :significance and wfo = :wfo
    """),
        params,
    )
    row = res.fetchone()
    cnt = row[0]
    sts = row[1]
    ets = row[2]
    if sts is None:
        raise NoDataFound("No Results Found, try flipping zone/county")

    res = conn.execute(
        sql_helper("""
     WITH coverage as (
        SELECT extract(year from issue) as yr, eventid,
        generate_series(issue at time zone :tzname,
                        expire at time zone :tzname, '1 minute'::interval) as s
                        from warnings where
        ugc = :ugc and phenomena = :phenomena and significance = :significance
        and wfo = :wfo),
      minutes as (SELECT distinct yr, eventid,
        (extract(hour from s)::numeric * 60. +
         extract(minute from s)::numeric) as m
        from coverage)

    SELECT minutes.m, count(*) from minutes GROUP by m
          """),
        params,
    )

    data = np.zeros((1440,), "f")
    for row in res:
        data[int(row[0])] = row[1]

    df = pd.DataFrame(
        dict(minute=pd.Series(np.arange(1440)), events=pd.Series(data))
    )

    vals = data / float(cnt) * 100.0
    title = (
        f"[{ugc}] {name} :: {vtec.get_ps_string(phenomena, significance)} "
        f"({phenomena}.{significance})\n"
        f"{cnt} Events - {sts:%Y-%m-%d %I:%M %p} to {ets:%Y-%m-%d %I:%M %p}"
    )

    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.bar(np.arange(1440), vals, ec="b", fc="b")
    if np.max(vals) > 50:
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.grid()
    ax.set_xticks(range(0, 1441, 60))
    ax.set_xticklabels(
        [
            "Mid",
            "",
            "",
            "3 AM",
            "",
            "",
            "6 AM",
            "",
            "",
            "9 AM",
            "",
            "",
            "Noon",
            "",
            "",
            "3 PM",
            "",
            "",
            "6 PM",
            "",
            "",
            "9 PM",
            "",
            "",
            "Mid",
        ]
    )
    ax.set_xlabel(f"Timezone: {tzname} (Daylight or Standard)")
    ax.set_ylabel(f"Frequency [%] out of {cnt} Events")
    ax.set_xlim(0, 1441)
    return fig, df
