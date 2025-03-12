"""
This chart presents the frequency of observed
minimum wind chill or maximum heat index over the period of
record for the observation site.  Please note that this application
requires the feels like temperature to be additive, so heat index
greater than air temperature and wind chill less than air temperature.
"""

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

from iemweb.util import month2months

PDICT = {
    "wcht": "Minimum Wind Chill",
    "heat": "Maximum Heat Index",
}
MDICT = {
    "all": "No Month/Time Limit",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="select",
            name="var",
            default="wcht",
            label="Which variable to analyze?",
            options=PDICT,
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Limit plot by month/season",
            options=MDICT,
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["zstation"]
    offset = 3 if ctx["month"] in ["all", "winter"] else 0
    months = month2months(ctx["month"])

    additive = "feel < tmpf" if ctx["var"] == "wcht" else "feel > tmpf"
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            sql_helper(
                """
            SELECT extract(year from valid + ':offset months'::interval)
                as year,
            min(feel) as min_feel, max(feel) as max_feel
            from alldata WHERE station = :station and {additive}
            and extract(month from valid) = ANY(:months)
            GROUP by year ORDER by year ASC
        """,
                additive=additive,
            ),
            conn,
            params={
                "offset": offset,
                "station": station,
                "months": months,
            },
            index_col="year",
        )
    if df.empty:
        raise NoDataFound("No data found.")

    ys = []
    freq = []
    sz = float(len(df.index))
    if ctx["var"] == "wcht":
        col = "min_feel"
        for lev in range(int(df[col].max()), int(df[col].min()) - 1, -1):
            freq.append(len(df[df[col] < lev].index) / sz * 100.0)
            ys.append(lev)
    else:
        col = "max_feel"
        for lev in range(int(df[col].min()), int(df[col].max()) + 1):
            freq.append(len(df[df[col] > lev].index) / sz * 100.0)
            ys.append(lev)
    ys = np.array(ys)

    title = (
        f"{ctx['_sname']} ({df.index[0]:.0f}-{df.index[-1]:.0f})\n"
        f"Frequency of Observed {PDICT[ctx['var']]} over {MDICT[ctx['month']]}"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1)

    color = "b" if ctx["var"] == "wcht" else "r"
    ax[0].barh(ys - 0.4, freq, ec=color, fc=color)
    ax[0].set_ylabel(f"{PDICT[ctx['var']]} " + r"$^\circ$F")
    ax[0].set_xlabel("Frequency [%]")
    ax[0].set_xticks([0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100])
    ax[0].grid(True)

    ax[1].bar(df.index.values, df[col], fc=color, ec=color)
    ax[1].set_ylim(bottom=df[col].min() - 5)
    ax[1].set_ylabel(f"{PDICT[ctx['var']]} " + r"$^\circ$F")
    ax[1].grid(True)
    if offset > 0:
        ax[1].set_xlabel("Year label for spring portion of season")

    return fig, df
