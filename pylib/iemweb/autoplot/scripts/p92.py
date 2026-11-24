"""
This map depicts the number of days since a
Weather Forecast Office has issued a given VTEC product.  You can
set the plot to a retroactive date, which computes the number of number
of days prior to that date.
"""

from datetime import date, timedelta
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot import pretty_bins
from pyiem.plot.geoplot import MapPlot
from pyiem.util import utc

from iemweb.autoplot.description import (
    CmapArg,
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
PDICT2 = {
    "single": "Select individual Phenomena/Significance event",
    "any": "Plot since issuance of any event",
}


class Params(AutoplotParams):
    """Request parameters."""

    limit: Annotated[
        str,
        SelectArg(
            options=PDICT2,
            label="Select Single or Any Event Type",
        ),
    ] = "single"
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
    cmap: Annotated[
        str,
        CmapArg(label="Select Color Map for Plot:"),
    ] = "viridis"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, cache=3600
    )


def plotter(ctx: Params):
    """Go"""
    phenomena = ctx.phenomena
    significance = ctx.significance
    edate = ctx.edate
    emerg_extra = " and is_emergency " if ctx.e == "yes" else ""
    sigph_limiter = "issue > :edatem1y "
    if ctx.limit == "single":
        sigph_limiter = "significance = :sig and phenomena = :phenom "
    with get_sqlalchemy_conn("postgis") as conn:
        if edate is not None:
            edate = utc(edate.year, edate.month, edate.day, 0, 0)
            res = conn.execute(
                sql_helper(
                    """
            select wfo, extract(days from (date(:edate) - max(issue))) as m,
            max(date(issue))
            from warnings where {sigph_limter} and issue < :edate {emerg_extra}
            GROUP by wfo ORDER by m ASC
            """,
                    emerg_extra=emerg_extra,
                    sigph_limter=sigph_limiter,
                ),
                {
                    "sig": significance,
                    "phenom": phenomena,
                    "edate": edate,
                    "edatem1y": edate - timedelta(days=365),
                },
            )
        else:
            res = conn.execute(
                sql_helper(
                    """
            select wfo, extract(days from ('TODAY'::date - max(issue))) as m,
            max(date(issue))
            from warnings where {sigph_limter}
            {emerg_extra} GROUP by wfo ORDER by m ASC
            """,
                    emerg_extra=emerg_extra,
                    sigph_limter=sigph_limiter,
                ),
                {
                    "sig": significance,
                    "phenom": phenomena,
                    "edatem1y": utc() - timedelta(days=365),
                },
            )
            edate = utc()
        data = {}
        rows = []
        for row in res:
            if row[0] not in ["HEB", "NHC"]:
                rows.append(dict(wfo=row[0], days=row[1], date_central=row[2]))
                data[row[0]] = max([row[1], 0])
    if not rows:
        raise NoDataFound("No Events Found")
    df = pd.DataFrame(rows).set_index("wfo")

    ee = " (Emergency) " if ctx.e == "yes" else ""
    title = vtec.get_ps_string(phenomena, significance)
    if ctx.limit == "any":
        title = "VTEC Event of Any Type"
    mp = MapPlot(
        sector="nws",
        axisbg="white",
        nocaption=True,
        apctx=ctx,
        title=(f"Days since Last {title}{ee} by NWS Office"),
        subtitle=f"Valid {edate:%d %b %Y %H%M} UTC",
    )
    mp.fill_cwas(
        data,
        bins=pretty_bins(0, max(1, int(df["days"].max()))),
        ilabel=True,
        units="Days",
        cmap=ctx.cmap,
        lblformat="%.0f",
        labelbuffer=0,
    )

    return mp.fig, df
