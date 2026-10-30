"""
This app generates maps of yearly USDA NASS county yield estimates.  It is a
bit of a work in progress yet, but will be added to as interest is shown!
"""

from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, centered_bins, pretty_bins
from pyiem.util import utc

from iemweb.autoplot.description import (
    CmapArg,
    CSectorArg,
    PlotDescription,
    SelectArg,
    YearArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {
    "corn": "Corn Grain",
    "soybeans": "Soybeans",
}
PDICT2 = {"yes": "Label counties with values", "no": "Don't show values "}
PDICT3 = {
    "departure": "Yield Departure from previous 10 year average",
    "value": "Yield",
}


class Params(AutoplotParams):
    """Request parameters."""

    year: Annotated[
        int,
        YearArg(
            min=1981,
            label="Select year to display",
            default=lambda: utc().year - 1,
        ),
    ]
    csector: Annotated[str, CSectorArg(label="Select state/sector")] = "IA"
    crop: Annotated[str, SelectArg(options=PDICT, label="Select Crop")] = (
        "corn"
    )
    var: Annotated[
        str, SelectArg(options=PDICT3, label="Select variable to plot")
    ] = "departure"
    ilabel: Annotated[
        str, SelectArg(label="Label Values?", options=PDICT2)
    ] = "yes"
    cmap: Annotated[str, CmapArg(label="Color Ramp:")] = "BrBG"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, nass=True
    )


def plotter(ctx: Params):
    """Go"""
    year1 = max(ctx.year - 10, 1981)
    params = {"y1": year1, "year": ctx.year, "crop": ctx.crop.upper()}
    params["util"] = "GRAIN"
    if ctx.crop == "soybeans":
        params["util"] = "ALL UTILIZATION PRACTICES"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
            with data as (
                select year, state_alpha || 'C' || county_ansi as ugc,
                avg(num_value) as num_value from
                nass_quickstats where county_ansi is not null and
                statisticcat_desc = 'YIELD' and commodity_desc = :crop and
                util_practice_desc = :util and year >= :y1 and year <= :year
                GROUP by year, ugc),
            agg as (
                select ugc, count(*), avg(num_value) from data
                WHERE year != :year group by ugc),
            y2022 as (
                select * from data where year = :year)
            select a.ugc, a.avg, a.count, y.num_value,
            y.num_value - a.avg as delta from agg a JOIN y2022 y on
            (a.ugc = y.ugc) ORDER by delta
            """
            ),
            conn,
            params=params,
            index_col="ugc",
        )
    if df.empty:
        raise NoDataFound("Could not find any data, sorry.")
    title = "Yield"
    col = "num_value"
    bins = pretty_bins(df[col].min(), df[col].max())
    if ctx.var == "departure":
        title = f"Yield Departure from {year1}-{ctx.year - 1} Average"
        col = "delta"
        bins = centered_bins(max(df[col].abs().max(), 50))
    mp = MapPlot(
        apctx=ctx,
        title=f"USDA NASS {ctx.crop.capitalize()} {ctx.year} {title}",
        stateborderwidth=3,
        nocaption=True,
    )
    mp.fill_ugcs(
        df[col].to_dict(),
        bins=bins,
        cmap=ctx.cmap,
        units="bu/ac",
        ilabel=ctx.ilabel == "yes",
        lblformat="%.1f",
        labelbuffer=1,
    )

    return mp.fig, df
