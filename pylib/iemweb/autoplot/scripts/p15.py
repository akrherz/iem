"""
This plot displays the directional frequency of
day to day changes in high or low temperature summarized by month.
"""

import calendar

import matplotlib.patheffects as PathEffects
import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, utc
from sqlalchemy import text

from iemweb.autoplot import ARG_STATION

PDICT = {"high": "High Temperature", "low": "Low Temperature"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="select",
            name="varname",
            default="high",
            label="Which metric to plot?",
            options=PDICT,
        ),
        dict(
            type="year",
            name="year",
            default=utc().year,
            label="Year to Highlight",
            min=1893,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["varname"]
    year = ctx["year"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text("""
        with obs as
        (select month, year, high, lag(high) OVER (ORDER by day ASC) as lhigh,
        low, lag(low) OVER (ORDER by day ASC) as llow
        from alldata where station = :station)

        SELECT year, month,
        sum(case when high > lhigh then 1 else 0 end)::numeric as high_greater,
        sum(case when high = lhigh then 1 else 0 end)::numeric as high_unch,
        sum(case when high < lhigh then 1 else 0 end)::numeric as high_lower,
        sum(case when low > llow then 1 else 0 end)::numeric as low_greater,
        sum(case when low = llow then 1 else 0 end)::numeric as low_unch,
        sum(case when low < llow then 1 else 0 end)::numeric as low_lower
        from obs GROUP by year, month ORDER by year, month
        """),
            conn,
            params={"station": station},
            index_col=None,
        )
    gdf = df.groupby("month").sum()
    gyear = df[df["year"] == year].groupby("month").sum()
    if gyear.empty or gdf.empty:
        raise NoDataFound("No data found.")
    increase = gdf[varname + "_greater"]
    nochange = gdf[varname + "_unch"]
    decrease = gdf[varname + "_lower"]
    increase2 = gyear[varname + "_greater"]
    nochange2 = gyear[varname + "_unch"]
    decrease2 = gyear[varname + "_lower"]

    title = f"{ctx['_sname']}\nDay to Day {varname.title()} Temperature Change"
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    total = decrease + nochange + increase
    total2 = decrease2 + nochange2 + increase2

    ax.bar(
        total.index.values - 0.2,
        decrease / total * 100.0,
        fc="b",
        label="Decrease",
        width=0.4,
        align="center",
    )
    ax.bar(
        total2.index.values + 0.2,
        decrease2 / total2 * 100.0,
        fc="lightblue",
        width=0.4,
        label=f"{year} ''",
        align="center",
    )
    ax.bar(
        total.index.values - 0.2,
        nochange / total * 100.0,
        bottom=(decrease / total * 100.0).values,
        fc="g",
        label="No Change",
        width=0.4,
        align="center",
    )
    ax.bar(
        total2.index.values + 0.2,
        nochange2 / total2 * 100.0,
        bottom=(decrease2 / total2 * 100.0).values,
        fc="lightgreen",
        width=0.4,
        label=f"{year} ''",
        align="center",
    )
    ax.bar(
        total.index.values - 0.2,
        increase / total * 100.0,
        bottom=((decrease + nochange) / total).values * 100.0,
        fc="r",
        width=0.4,
        label="Increase",
        align="center",
    )
    ax.bar(
        total2.index.values + 0.2,
        increase2 / total2 * 100.0,
        bottom=((decrease2 + nochange2) / total2).values * 100.0,
        fc="pink",
        width=0.4,
        label=f"{year} ''",
        align="center",
    )

    offset = -0.2
    for _df in [gdf, gyear]:
        increase = _df[varname + "_greater"]
        nochange = _df[varname + "_unch"]
        decrease = _df[varname + "_lower"]
        total = decrease + nochange + increase
        for i, _ in _df.iterrows():
            txt = ax.text(
                i + offset,
                decrease[i] / total[i] * 100.0 - 5,
                f"{(decrease[i] / total[i] * 100.0):.0f}",
                ha="center",
                fontsize=10,
            )
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=2, foreground="white")]
            )
            ymid = (decrease[i] + (nochange[i] / 2.0)) / total[i] * 100.0
            txt = ax.text(
                i + offset,
                ymid,
                f"{(nochange[i] / total[i] * 100.0):.0f}",
                ha="center",
                va="center",
                fontsize=10,
            )
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=2, foreground="white")]
            )
            txt = ax.text(
                i + offset,
                (decrease[i] + nochange[i]) / total[i] * 100.0 + 2,
                f"{(increase[i] / total[i] * 100.0):.0f}",
                ha="center",
                fontsize=10,
            )
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=2, foreground="white")]
            )
        offset += 0.4

    ax.set_xticks(np.arange(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.legend(ncol=3, fontsize=12, loc=9, framealpha=1)
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_ylabel("Percentage of Days [%]")
    ax.set_xlabel(
        f"Dark Shades are long term averages, lighter are {year} actuals"
    )

    return fig, df
