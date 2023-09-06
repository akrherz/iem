"""
This map depicts the number of days since a
Weather Forecast Office has issued a given VTEC product.  You can
set the plot to a retroactive date, which computes the number of number
of days prior to that date.
"""
import datetime

import pandas as pd
import psycopg2.extras
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn, utc

PDICT = {
    "yes": "Only Emergencies",
    "all": "All Events",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 3600}
    desc["arguments"] = [
        dict(
            type="phenomena",
            name="phenomena",
            default="TO",
            label="Select Watch/Warning Phenomena Type:",
        ),
        dict(
            type="significance",
            name="significance",
            default="W",
            label="Select Watch/Warning Significance Level:",
        ),
        dict(
            type="select",
            options=PDICT,
            default="all",
            label="For TOR/FFW Warnings, plot emergencies?",
            name="e",
        ),
        dict(
            type="date",
            default=datetime.date.today().strftime("%Y/%m/%d"),
            optional=True,
            label="Retroactive Date of Plot:",
            name="edate",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    bins = [0, 1, 14, 31, 91, 182, 273, 365, 730, 1460, 2920, 3800]
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    edate = ctx.get("edate")
    emerg_extra = ""
    if ctx["e"] == "yes":
        emerg_extra = " and is_emergency "
    if edate is not None:
        edate = utc(edate.year, edate.month, edate.day, 0, 0)
        cursor.execute(
            f"""
         select wfo,  extract(days from (%s::date - max(issue))) as m,
         max(date(issue))
         from warnings where significance = %s and phenomena = %s
         and issue < %s {emerg_extra}
         GROUP by wfo ORDER by m ASC
        """,
            (edate, significance, phenomena, edate),
        )
    else:
        cursor.execute(
            f"""
         select wfo,  extract(days from ('TODAY'::date - max(issue))) as m,
         max(date(issue))
         from warnings where significance = %s and phenomena = %s {emerg_extra}
         GROUP by wfo ORDER by m ASC
        """,
            (significance, phenomena),
        )
        edate = utc()

    if cursor.rowcount == 0:
        raise NoDataFound(
            "No Events Found for "
            f"{vtec.get_ps_string(phenomena, significance)} "
            f"({phenomena}.{significance})"
        )
    data = {}
    rows = []
    for row in cursor:
        wfo = row[0] if row[0] != "JSJ" else "SJU"
        rows.append(dict(wfo=wfo, days=row[1], date_central=row[2]))
        data[wfo] = max([row[1], 0])
    df = pd.DataFrame(rows)
    df = df.set_index("wfo")

    ee = " (Emergency) " if ctx["e"] == "yes" else ""
    mp = MapPlot(
        sector="nws",
        axisbg="white",
        nocaption=True,
        apctx=ctx,
        title=(
            f"Days since Last {vtec.get_ps_string(phenomena, significance)}"
            f"{ee} by NWS Office"
        ),
        subtitle=f"Valid {edate:%d %b %Y %H%M} UTC",
    )
    mp.fill_cwas(
        data,
        bins=bins,
        ilabel=True,
        units="Days",
        lblformat="%.0f",
        labelbuffer=0,
    )

    return mp.fig, df


if __name__ == "__main__":
    plotter({})
