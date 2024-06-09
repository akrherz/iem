"""This chart presents crop condition reports from USDA/NASS."""

import calendar
import datetime

import pandas as pd
from matplotlib.font_manager import FontProperties
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

NASS_CROP_PROGRESS = {
    "corn_poor_verypoor": "Percentage Corn Poor + Very Poor Condition",
    "corn_good_excellent": "Percentage Corn Good + Excellent Condition",
    "corn_harvest": "Percentage Corn Harvested (Grain) Acres",
    "corn_planting": "Percentage Corn Planted Acres",
    "corn_silking": "Percentage Corn Silking Acres",
    "soybeans_poor_verypoor": "Percentage Soybean Poor + Very Poor Condition",
    "soybeans_good_excellent": "Percentage Soybean Good + Excellent Condition",
    "soybeans_planting": "Percentage Soybean Planted Acres",
    "soybeans_harvest": "Percentage Soybean Harvested Acres",
    "soil_short_veryshort": "Percentage Topsoil Moisture Short + Very Short",
}

NASS_CROP_PROGRESS_LOOKUP = {
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
    "soybeans_poor_verypoor": [
        "SOYBEANS - CONDITION, MEASURED IN PCT POOR",
        "SOYBEANS - CONDITION, MEASURED IN PCT VERY POOR",
    ],
    "soybeans_good_excellent": [
        "SOYBEANS - CONDITION, MEASURED IN PCT GOOD",
        "SOYBEANS - CONDITION, MEASURED IN PCT EXCELLENT",
    ],
    "soil_short_veryshort": [
        "SOIL, TOPSOIL - MOISTURE, MEASURED IN PCT VERY SHORT",
        "SOIL, TOPSOIL - MOISTURE, MEASURED IN PCT SHORT",
    ],
}
PDICT = {
    "six": "Plot all six states",
    "one": "Plot just state #1",
}
PDICT2 = {
    "all": "Plot all available years",
    "s": "Plot only selected years",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "nass": True}
    desc["arguments"] = [
        dict(
            type="select",
            name="w",
            default="six",
            options=PDICT,
            label="How many states to plot:",
        ),
        dict(type="state", name="st1", default="IA", label="Select State #1:"),
        dict(type="state", name="st2", default="IL", label="Select State #2:"),
        dict(type="state", name="st3", default="MN", label="Select State #3:"),
        dict(type="state", name="st4", default="WI", label="Select State #4:"),
        dict(type="state", name="st5", default="MO", label="Select State #5:"),
        dict(type="state", name="st6", default="IN", label="Select State #6:"),
        dict(
            type="select",
            name="y",
            default="all",
            options=PDICT2,
            label="How many years to plot:",
        ),
        dict(
            type="year",
            min=1981,
            name="y1",
            default=datetime.date.today().year,
            label="Select Year #1",
        ),
        dict(
            type="year",
            min=1981,
            name="y2",
            optional=True,
            default=2012,
            label="Select Year #2",
        ),
        dict(
            type="year",
            min=1981,
            name="y3",
            optional=True,
            default=2008,
            label="Select Year #3",
        ),
        dict(
            type="year",
            min=1981,
            name="y4",
            optional=True,
            default=1993,
            label="Select Year #4",
        ),
        dict(
            type="select",
            name="var",
            default="corn_poor_verypoor",
            options=NASS_CROP_PROGRESS,
            label="Which Crop Progress Report?",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    st1 = ctx["st1"][:2]
    st2 = ctx["st2"][:2]
    st3 = ctx["st3"][:2]
    st4 = ctx["st4"][:2]
    st5 = ctx["st5"][:2]
    st6 = ctx["st6"][:2]
    y1 = ctx["y1"]
    y2 = ctx.get("y2")
    y3 = ctx.get("y3")
    y4 = ctx.get("y4")
    years = [y1, y2, y3, y4]
    states = [st1, st2, st3, st4, st5, st6]
    varname = ctx["var"]
    desc = NASS_CROP_PROGRESS_LOOKUP[varname]
    if not isinstance(desc, list):
        desc = [
            desc,
        ]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                "select extract(year from week_ending) as year, week_ending, "
                "sum(num_value) as value, state_alpha "
                "from nass_quickstats where short_desc = ANY(:desc) and "
                "num_value is not null and state_alpha = ANY(:states) "
                "GROUP by year, week_ending, state_alpha "
                "ORDER by state_alpha, week_ending"
            ),
            conn,
            params={
                "states": states,
                "desc": desc,
            },
            index_col=None,
            parse_dates="week_ending",
        )
    if df.empty:
        raise NoDataFound("ERROR: No data found!")
    df["doy"] = pd.to_numeric(df["week_ending"].dt.strftime("%j"))
    prop = FontProperties(size=10)

    title = (
        f"{NASS_CROP_PROGRESS[varname]} "
        f"({df['year'].min():.0f} till {df['week_ending'].max():%-d %b %Y})"
    )
    fig = figure(
        title=title,
        subtitle="USDA/NASS Weekly Crop Condition Report",
        apctx=ctx,
    )
    width = 0.28
    height = 0.32
    x0 = 0.08
    xpad = 0.03
    y0 = 0.07
    y1 = 0.51
    if ctx["w"] == "one":
        axes = [
            [fig.add_axes([x0, 0.12, 0.9, 0.75]), None, None],
            [None, None, None],
        ]
    else:
        axes = [
            [
                fig.add_axes([x0, y1, width, height]),
                fig.add_axes([x0 + width + xpad, y1, width, height]),
                fig.add_axes([x0 + 2 * width + 2 * xpad, y1, width, height]),
            ],
            [
                fig.add_axes([x0, y0, width, height]),
                fig.add_axes([x0 + width + xpad, y0, width, height]),
                fig.add_axes([x0 + 2 * width + 2 * xpad, y0, width, height]),
            ],
        ]

    xticks = (1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
    i = 0
    for col in range(3):
        for row in range(2):
            ax = axes[row][col]
            if ax is None:
                continue
            state = states[i]
            df2 = df[df["state_alpha"] == state]
            if df2.empty:
                continue
            colors = ["black", "green", "blue", "red"]

            for year, gdf in df2.groupby("year"):
                if ctx["y"] != "all" and year not in years:
                    continue
                ax.plot(
                    gdf["doy"],
                    gdf["value"],
                    c="tan" if year not in years else colors.pop(),
                    lw=3 if year in years else 1,
                    zorder=5 if year in years else 3,
                    label=f"{year:.0f}" if year in years else None,
                )
            if row == 0 and col == 0 and ctx["w"] == "one":
                ax.legend(ncol=5, loc=(0.35, -0.1), prop=prop)
            if row == 0 and col == 1:
                ax.legend(ncol=5, loc=(0.4, -0.25), prop=prop)
            ax.set_xticks(xticks)
            ax.set_xticklabels(calendar.month_abbr[1:])
            ax.set_xlim(df["doy"].min() - 5, df["doy"].max() + 5)
            ax.grid(True)
            ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
            ax.set_ylim(0, 100)
            if col == 0:
                ax.set_ylabel("Coverage [%]")
            ax.text(
                0,
                1.0,
                state_names[state],
                ha="left",
                va="bottom",
                size=16,
                transform=ax.transAxes,
            )
            i += 1

    return fig, df
