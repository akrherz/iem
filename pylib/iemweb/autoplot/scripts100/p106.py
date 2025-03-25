"""
This plot displays hourly temperature distributions on dates having at
least one hourly observation meeting the given requirement.  The
distributions are presented as "violins" with the width of the violin
providing some insight into the population density at the given
temperature.
"""

from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.util import month2months

PDICT = {
    "tmpf_above": "Temperature At or Above Threshold (F)",
    "tmpf_below": "Temperature Below Threshold (F)",
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
    desc = {"description": __doc__}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="select",
            name="opt",
            default="tmpf_above",
            label="Criterion?",
            options=PDICT,
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="int",
            name="threshold",
            default="80",
            label="Temperature Threshold (F):",
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["zstation"]
    threshold = ctx["threshold"]
    opt = ctx["opt"]
    month = ctx["month"]

    months = month2months(month)

    if opt == "tmpf_above":
        limiter = "round(tmpf::numeric,0) >= :threshold"
    else:
        limiter = "round(tmpf::numeric,0) < :threshold"

    with get_sqlalchemy_conn("asos") as conn:
        res = conn.execute(
            sql_helper(
                """
            WITH obs as (
                SELECT valid, tmpf from alldata WHERE
                station = :station and extract(month from valid) = ANY(:months)
                and tmpf > -80
            ),
            events as (
                SELECT distinct date(valid at time zone :tzname) from obs
                WHERE {limiter})
        SELECT valid at time zone :tzname + '10 minutes'::interval, tmpf
        from obs a JOIN events e on
        (date(a.valid at time zone :tzname) = e.date)
        """,
                limiter=limiter,
            ),
            {
                "station": station,
                "threshold": threshold,
                "months": months,
                "tzname": ctx["_nt"].sts[station]["tzname"],
            },
        )
        data = [[] for _ in range(24)]
        if res.rowcount == 0:
            raise NoDataFound("Failed to find any data for station.")
        for row in res:
            data[row[0].hour].append(row[1])

    title = (
        f"{ctx['_sname']} :: Hourly Temp "
        f"Distributions over ({month.capitalize()})"
    )
    subtitle = (
        f"On Dates with at least one temperature ob {PDICT[opt]} "
        f"{threshold:.0f}"
    )
    fig, ax = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    v1 = ax.violinplot(data, showextrema=True, showmeans=True, widths=0.7)
    for lbl in ["cmins", "cmeans", "cmaxes"]:
        v1[lbl].set_color("r")

    ax.grid(True)
    ax.set_ylabel(r"Temperature $^\circ$F")
    ax.set_xlabel(
        f"Local Hour for Timezone: {ctx['_nt'].sts[station]['tzname']}"
    )
    ax.set_xticks(range(1, 25, 3))
    ax.set_xticklabels("Mid,3 AM,6 AM,9 AM,Noon,3 PM,6 PM,9 PM".split(","))
    return fig
