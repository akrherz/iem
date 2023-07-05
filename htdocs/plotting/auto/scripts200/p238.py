"""
This app generates maps of yearly USDA NASS county yield estimates.  It is a
bit of a work in progress yet, but will be added to as interest is shown!
"""

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc
from sqlalchemy import text

PDICT = {
    "corn": "Corn Grain",
}
PDICT2 = {"yes": "Label counties with values", "no": "Don't show values "}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "nass": True}
    desc["arguments"] = [
        {
            "type": "year",
            "min": 1981,
            "default": utc().year - 1,
            "name": "year",
            "label": "Select year to display",
        },
        {
            "type": "csector",
            "name": "csector",
            "default": "IA",
            "label": "Select state/sector",
        },
        {
            "type": "select",
            "label": "Label Values?",
            "default": "yes",
            "options": PDICT2,
            "name": "ilabel",
        },
        dict(type="cmap", name="cmap", default="BrBG", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    year1 = max(ctx["year"] - 10, 1981)
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                """
            with data as (
                select year, state_alpha || 'C' || county_ansi as ugc,
                avg(num_value) as num_value from
                nass_quickstats where county_ansi is not null and
                statisticcat_desc = 'YIELD' and commodity_desc = 'CORN' and
                util_practice_desc = 'GRAIN' and year >= :y1 and year <= :year
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
            params={"y1": year1, "year": ctx["year"]},
            index_col="ugc",
        )
    if df.empty:
        raise NoDataFound("Could not find any data, sorry.")
    mp = MapPlot(
        apctx=ctx,
        title=(
            f"USDA NASS {ctx['year']} Corn Yield Deparature from "
            f"{year1}-{ctx['year'] - 1} Average"
        ),
        stateborderwidth=3,
        nocaption=True,
    )
    mp.fill_ugcs(
        df["delta"].to_dict(),
        bins=range(-50, 51, 10),
        cmap=ctx["cmap"],
        units="bu/ac",
        ilabel=ctx["ilabel"] == "yes",
        lblformat="%.1f",
        labelbuffer=1,
    )

    return mp.fig, df


if __name__ == "__main__":
    plotter({})
