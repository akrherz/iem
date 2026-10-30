"""
This autoplot is a bit of a catch-all for mapping event counts at a WFO or
CWSU map unit.  These are events that do not have VTEC.
"""

from datetime import UTC, datetime
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import MapPlot, pretty_bins
from pyiem.util import utc

from iemweb.autoplot.description import (
    CmapArg,
    DateTimeArg,
    PlotDescription,
    SelectArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {
    "sps": "Special Weather Statements (SPS) with polygons",
    "cwa": "CWSU Center Weather Advisories (CWA)",
}


class Params(AutoplotParams):
    """Request parameters."""

    sts: Annotated[
        datetime,
        DateTimeArg(
            label="Start Timestamp (UTC):",
            min="1986/01/01 0000",
            default=lambda: (
                utc().replace(month=1, day=1).strftime("%Y/%m/%d 0000")
            ),
        ),
    ]
    ets: Annotated[
        datetime,
        DateTimeArg(
            label="End Timestamp (UTC):",
            min="1986/01/01 0000",
            max=lambda: utc().strftime("%Y/%m/%d 2359"),
            default=lambda: utc().strftime("%Y/%m/%d %H%M"),
        ),
    ]
    w: Annotated[
        str, SelectArg(options=PDICT, label="Which Event Type to Total")
    ] = "sps"
    cmap: Annotated[str, CmapArg(label="Color Ramp:")] = "Greens"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    sts = ctx.sts.replace(tzinfo=UTC)
    ets = ctx.ets.replace(tzinfo=UTC)
    params = {}
    params["sts"] = sts
    params["ets"] = ets

    title = f"{PDICT[ctx.w]} Event Count"
    subtitle = (
        f"For issuance between {sts:%Y-%m-%d %H:%M} UTC "
        f"to {ets:%Y-%m-%d %H:%M} UTC"
    )
    sql = """
    SELECT wfo as datum, count(*) from sps where issue >= :sts and issue < :ets
    and not ST_IsEmpty(geom) GROUP by datum
    """
    if ctx.w == "cwa":
        sql = """
        SELECT center as datum, count(*) from cwas
        WHERE issue >= :sts and issue < :ets GROUP by datum
        """
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            sql_helper(sql),
            conn,
            params=params,
            index_col="datum",
        )
    mp = MapPlot(
        sector="nws",
        title=title,
        subtitle=subtitle,
    )
    func = mp.fill_cwsu if ctx.w == "cwa" else mp.fill_cwas
    bins = list(range(0, 101, 10))
    if not df.empty:
        bins = pretty_bins(0, df["count"].max())
    func(
        df["count"],
        cmap=ctx.cmap,
        ilabel=True,
        lblformat="%.0f",
        bins=bins,
        extend="neither",
    )
    return mp.fig, df
