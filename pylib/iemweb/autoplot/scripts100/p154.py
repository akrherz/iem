"""
This chart presents an average hourly value for
a given month or season over the years covering the period of record
for the site.  For the year to plot, at least 80% data availability needs
to be obtained.
"""

import datetime

import pandas as pd
from matplotlib.font_manager import FontProperties
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from scipy import stats
from sqlalchemy import text

from iemweb.util import month2months

PDICT = {"avg_tmpf": "Average Temperature"}
UNITS = {"avg_tmpf": "F"}
MDICT = {
    "all": "No Month Limit",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "gs": "1 May to 30 Sep",
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
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            options=MDICT,
            label="Select Month/Season/All",
        ),
        dict(
            type="hour",
            name="hour",
            default=20,
            label="At Time (Local Timezone of Station):",
        ),
        dict(
            type="select",
            name="var",
            options=PDICT,
            default="avg_tmpf",
            label="Which Variable to Plot",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    font0 = FontProperties()
    font0.set_family("monospace")
    font0.set_size(16)

    ctx = get_autoplot_context(fdict, get_description())
    varname = ctx["var"]
    month = ctx["month"]
    station = ctx["zstation"]
    hour = ctx["hour"]
    months = month2months(month)

    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                """
        WITH obs as (
            SELECT (valid + '10 minutes'::interval) at time zone :tzname as ts,
            tmpf::int as itmpf, dwpf::int as idwpf from alldata
            where station = :station and tmpf is not null
            and dwpf is not null and
            extract(month from valid at time zone :tzname) = ANY(:months)),
        agg1 as (
            SELECT date_trunc('hour', ts) as hts, avg(itmpf) as avg_itmpf,
            avg(idwpf) as avg_idwpf from obs
            WHERE extract(hour from ts) = :hour GROUP by hts)

        SELECT extract(year from hts)::int as year, avg(avg_itmpf) as avg_tmpf,
        count(*) as cnt
        from agg1 GROUP by year ORDER by year ASC
        """
            ),
            conn,
            params={
                "tzname": ctx["_nt"].sts[station]["tzname"],
                "station": station,
                "months": months,
                "hour": hour,
            },
            index_col="year",
        )
    if df.empty:
        raise NoDataFound("No data was found.")
    minfreq = len(months) * 30 * 0.8
    df2 = df[df["cnt"] > minfreq]
    lts = datetime.datetime(2000, 1, 1, int(hour), 0)
    title = (
        f"{ctx['_sname']}:: {lts:%-I %p} Local "
        f"({df2.index.min()}-{df2.index.max()})"
    )
    subtitle = f"{PDICT[varname]} [{MDICT[month]}]"
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    ax.bar(df2.index.values, df2[varname], align="center", ec="b", fc="b")
    m = df2[varname].mean()
    ax.axhline(m, lw=2, zorder=5, color="k")
    slp, intercept, r, _, _ = stats.linregress(
        df2.index.values, df2[varname].values
    )
    ax.plot(
        df2.index.values,
        intercept + (df2.index.values * slp),
        color="r",
        lw=2,
        zorder=6,
    )
    ax.text(
        0.02,
        0.92,
        r"$\frac{^\circ}{decade} = %.2f,R^2=%.2f, avg = %.1f$"
        % (slp * 10.0, r**2, m),
        va="bottom",
        transform=ax.transAxes,
        bbox=dict(color="white"),
    )

    ax.set_ylim([df2[varname].min() - 5, df2[varname].max() + 5])
    ax.grid(True)

    return fig, df
