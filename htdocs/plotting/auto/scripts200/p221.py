"""Plot of yearly NASS timeseries"""
import datetime
import calendar

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.reference import state_names
from pyiem.exceptions import NoDataFound

PDICT = {
    "corn_poor_verypoor": "Percentage Corn Poor + Very Poor Condition",
    "corn_good_excellent": "Percentage Corn Good + Excellent Condition",
    "corn_harvest": "Percentage Corn Harvested (Grain) Acres",
    "corn_planting": "Percentage Corn Planted Acres",
    "corn_silking": "Percentage Corn Silking Acres",
    "soybeans_planting": "Percentage Soybean Planted Acres",
    "soybeans_harvest": "Percentage Soybean Harvested Acres",
    "soil_short_veryshort": "Percentage Topsoil Moisture Short + Very Short",
}
LOOKUP = {
    "corn_planting": "CORN - PROGRESS, MEASURED IN PCT PLANTED",
    "corn_harvest": "CORN, GRAIN - PROGRESS, MEASURED IN PCT HARVESTED",
    "soybeans_planting": "SOYBEANS - PROGRESS, MEASURED IN PCT PLANTED",
    "soybeans_harvest": "SOYBEANS - PROGRESS, MEASURED IN PCT HARVESTED",
    "corn_silking": "CORN - PROGRESS, MEASURED IN PCT SILKING",
    "corn_poor_verypoor": [
        "CORN - CONDITION, MEASURED IN PCT POOR",
        "CORN - CONDITION, MEASURED IN PCT VERY POOR",
    ],
    "corn_good_excellent": [
        "CORN - CONDITION, MEASURED IN PCT GOOD",
        "CORN - CONDITION, MEASURED IN PCT EXCELLENT",
    ],
    "soil_short_veryshort": [
        "SOIL, TOPSOIL - MOISTURE, MEASURED IN PCT VERY SHORT",
        "SOIL, TOPSOIL - MOISTURE, MEASURED IN PCT SHORT",
    ],
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc["nass"] = True
    desc[
        "description"
    ] = """This plot presents yearly time series of a statewide NASS
    metric."""
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT,
            default="corn_planting",
            name="var",
            label="Available variables to plot:",
        ),
        dict(
            type="year",
            minval=1981,
            default=datetime.date.today().year,
            label="Which year to highlight?",
            name="year",
        ),
        dict(
            type="year",
            name="year2",
            minval=1981,
            default=1988,
            optional=True,
            label="Highlight additional year (optional):",
        ),
        dict(
            type="year",
            name="year3",
            minval=1981,
            default=1993,
            optional=True,
            label="Highlight additional year (optional)",
        ),
        dict(
            type="year",
            name="year4",
            minval=2012,
            default=today.year - 1,
            optional=True,
            label="Highlight additional year (optional)",
        ),
        dict(
            type="state",
            default="IA",
            label="Which state to plot for?",
            name="state",
        ),
    ]
    return desc


def get_df(ctx):
    """Figure out what data we need to fetch here"""
    varname = ctx["var"]
    pgconn = get_dbconn("coop")
    params = LOOKUP[varname]
    if isinstance(params, list):
        dlimit = " short_desc in %s" % (str(tuple(params)),)
    else:
        dlimit = " short_desc = '%s' " % (params,)
    # NB aggregate here needed for the multiple parameter short_desc above
    df = read_sql(
        "select year, week_ending, sum(num_value) as value "
        f"from nass_quickstats where {dlimit} and num_value is not null and "
        "state_alpha = %s "
        "GROUP by year, week_ending "
        "ORDER by week_ending",
        pgconn,
        params=(ctx["state"],),
        index_col=None,
        parse_dates="week_ending",
    )
    if df.empty:
        raise NoDataFound("No NASS Data was found for query, sorry.")
    df["doy"] = pd.to_numeric(df["week_ending"].dt.strftime("%j"))
    ctx["df"] = df
    ctx["title"] = "%s USDA NASS %s" % (
        state_names[ctx["state"]],
        PDICT[varname],
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    year2 = ctx.get("year2", 0)
    year3 = ctx.get("year3", 0)
    year4 = ctx.get("year4", 0)
    wantedyears = [ctx["year"], year2, year3, year4]
    yearcolors = ["r", "g", "b", "purple"]

    get_df(ctx)
    fig, ax = figure_axes(title=ctx["title"])
    for year, gdf in ctx["df"].groupby("year"):
        color = "red" if year == ctx["year"] else "tan"
        label = str(year) if year in wantedyears else None
        if year in wantedyears:
            color = yearcolors[wantedyears.index(year)]
            lw = 2
        else:
            lw = 1
            color = "tan"
        ax.plot(gdf["doy"], gdf["value"], color=color, label=label, lw=lw)

    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.legend(ncol=4)
    ax.set_ylabel("Percentage")
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 100])
    ax.set_xlim(
        ctx["df"]["doy"].min() - 5,
        ctx["df"]["doy"].max() + 5,
    )
    return fig, ctx["df"]


if __name__ == "__main__":
    plotter({})
