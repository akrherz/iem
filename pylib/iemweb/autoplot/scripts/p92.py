"""
This map depicts the number of days since a
Weather Forecast Office has issued a given VTEC product.  You can
set the plot to a retroactive date, which computes the number of number
of days prior to that date.
"""

from datetime import date
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot.geoplot import MapPlot
from pyiem.util import utc

from iemweb.autoplot.description import (
    DateArg,
    PhenomenaArg,
    PlotDescription,
    SelectArg,
    SignificanceArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {
    "yes": "Only Emergencies",
    "all": "All Events",
}


class Params(AutoplotParams):
    """Request parameters."""

    phenomena: Annotated[
        str, PhenomenaArg(label="Select Watch/Warning Phenomena Type:")
    ] = "TO"
    significance: Annotated[
        str,
        SignificanceArg(label="Select Watch/Warning Significance Level:"),
    ] = "W"
    e: Annotated[
        str,
        SelectArg(
            options=PDICT, label="For TOR/FFW Warnings, plot emergencies?"
        ),
    ] = "all"
    edate: Annotated[
        date | None,
        DateArg(
            label="Retroactive Date of Plot:",
            default=lambda: date.today().strftime("%Y/%m/%d"),
        ),
    ] = None


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, cache=3600
    )


def plotter(ctx: Params):
    """Go"""
    bins = [0, 1, 14, 31, 91, 182, 273, 365, 730, 1460, 2920, 3800]
    phenomena = ctx.phenomena
    significance = ctx.significance
    edate = ctx.edate
    emerg_extra = " and is_emergency " if ctx.e == "yes" else ""
    with get_sqlalchemy_conn("postgis") as conn:
        if edate is not None:
            edate = utc(edate.year, edate.month, edate.day, 0, 0)
            res = conn.execute(
                sql_helper(
                    """
            select wfo,  extract(days from (date(:edate) - max(issue))) as m,
            max(date(issue))
            from warnings where significance = :sig and phenomena = :phenom
            and issue < :edate {emerg_extra}
            GROUP by wfo ORDER by m ASC
            """,
                    emerg_extra=emerg_extra,
                ),
                {
                    "sig": significance,
                    "phenom": phenomena,
                    "edate": edate,
                },
            )
        else:
            res = conn.execute(
                sql_helper(
                    """
            select wfo,  extract(days from ('TODAY'::date - max(issue))) as m,
            max(date(issue))
            from warnings where significance = :sig and phenomena = :phenom
            {emerg_extra} GROUP by wfo ORDER by m ASC
            """,
                    emerg_extra=emerg_extra,
                ),
                {"sig": significance, "phenom": phenomena},
            )
            edate = utc()

        if res.rowcount == 0:
            raise NoDataFound(
                "No Events Found for "
                f"{vtec.get_ps_string(phenomena, significance)} "
                f"({phenomena}.{significance})"
            )
        data = {}
        rows = []
        for row in res:
            rows.append(dict(wfo=row[0], days=row[1], date_central=row[2]))
            data[row[0]] = max([row[1], 0])
    df = pd.DataFrame(rows)
    df = df.set_index("wfo")

    ee = " (Emergency) " if ctx.e == "yes" else ""
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
