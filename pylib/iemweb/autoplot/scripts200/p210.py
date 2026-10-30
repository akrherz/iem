"""
This application generates a map of the per WFO office usage of a
given text product identifier based on unofficial IEM archives of NWS
Text Product data.  The three character IDs presented here are sometimes
called the AWIPS ID or AFOS ID.</p>

<p>If you pick the "Year of First/Last Issuance",
please be careful with the
start datetime setting as it will floor the time period that products
are searched for.</p>

<p>The IEM Archives are generally reliable back to 2001, so please note
that any 2001 values plotted on the map as the first year would be a false
positive.</p>

<p>Running a plot for multiple years of data will be somewhat slow
(30+ seconds), so please be patient with it!</p>

<p><a href="?q=235">Autoplot 235</a> presents a monthly/yearly chart of
issuance counts for a single Weather Forecast Offices.</p>
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot.geoplot import MapPlot
from pyiem.util import utc

from iemweb.autoplot import ensure_prodDefinitions_key_in_label
from iemweb.autoplot.description import (
    CmapArg,
    DateTimeArg,
    PlotDescription,
    SelectArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {
    "count": "Issuance Count",
    "last": "Year of Last Issuance",
    "first": "Year of First Issuance",
}
PDICT2 = {
    "cwsu": "Center Weather Service Unit (CWSU)",
    "rfc": "River Forecast Center (RFC)",
    "cwa": "Weather Forecast Office (WFO) / CWA",
}


def _now() -> datetime:
    """Tomorrow, so that the current UTC day is fully included."""
    return utc() + timedelta(days=1)


class Params(AutoplotParams):
    """Request parameters."""

    pil: Annotated[
        str,
        SelectArg(
            options=ensure_prodDefinitions_key_in_label(),
            label="Select 3 Character Product ID (AWIPS ID / AFOS)",
        ),
    ] = "AFD"
    var: Annotated[
        str, SelectArg(options=PDICT, label="Statistic to Plot")
    ] = "count"
    w: Annotated[str, SelectArg(options=PDICT2, label="Summarize by:")] = "cwa"
    sts: Annotated[
        datetime,
        DateTimeArg(
            label="Search archive starting at (UTC Timestamp):",
            min="2001/01/01 0000",
            default=lambda: _now().strftime("%Y/01/01 0000"),
        ),
    ]
    ets: Annotated[
        datetime,
        DateTimeArg(
            label="Search archive ending at (UTC Timestamp):",
            min="2001/01/01 0000",
            max=lambda: _now().strftime("%Y/%m/%d 2359"),
            default=lambda: _now().strftime("%Y/%m/%d 0000"),
        ),
    ]
    cmap: Annotated[str, CmapArg(label="Color Ramp:")] = "jet"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", cache=300, data=True
    )


def plotter(ctx: Params):
    """Go"""
    sts = ctx.sts.replace(tzinfo=UTC)
    ets = min(ctx.ets.replace(tzinfo=UTC), utc())
    prod_defs = ensure_prodDefinitions_key_in_label()
    pil = ctx.pil[:3]

    with get_sqlalchemy_conn("afos") as conn:
        df = pd.read_sql(
            sql_helper("""
    SELECT source, pil, min(entered at time zone 'UTC') as first,
    max(entered at time zone 'UTC') as last, count(*) from products
    WHERE substr(pil, 1, 3) = :pil and entered >= :sts and entered < :ets
    GROUP by source, pil ORDER by source, pil ASC"""),
            conn,
            params={"pil": pil, "sts": sts, "ets": ets},
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No text products found for query, sorry.")

    data = {}
    subtitle = ""
    if ctx.var == "count":
        gdf = df.groupby("source").sum(numeric_only=True)  # dt makes no sense
        subtitle = f"Total: {gdf['count'].sum():,.0f}"
    elif ctx.var == "last":
        gdf = df.groupby("source").max()
    else:  # first
        gdf = df.groupby("source").min()
    minval = 1
    maxval = gdf["count"].max()
    if ctx.var in ["last", "first"]:
        minval = gdf[ctx.var].min().year
        maxval = gdf[ctx.var].max().year
    if (maxval - minval) < 10:
        bins = range(minval - 1, maxval + 2)
    else:
        bins = np.linspace(minval, maxval + 2, 10, dtype="i")
    for source, row in gdf.iterrows():
        if source == "PABR":
            continue
        key = source[1:]
        if ctx.var == "count":
            data[key] = row["count"]
        else:
            data[key] = row[ctx.var].year

    mp = MapPlot(
        apctx=ctx,
        title=f"NWS {PDICT[ctx.var]} of {prod_defs.get(pil, pil)}",
        subtitle=(
            f"Plot valid between {sts:%d %b %Y %H:%M} UTC "
            f"and {ets:%d %b %Y %H:%M} UTC, "
            f"based on unofficial IEM Archives.{subtitle}"
        ),
        sector="nws",
        nocaption=True,
    )
    func = {
        "cwa": mp.fill_cwas,
        "cwsu": mp.fill_cwsu,
        "rfc": mp.fill_rfc,
    }
    func[ctx.w](
        data,
        ilabel=True,
        lblformat="%.0f",
        cmap=ctx.cmap,
        extend="neither",
        bins=bins,
        units="count" if ctx.var == "count" else "year",
        labelbuffer=0,
    )
    return mp.fig, df
