"""
This plot displays hourly variable distributions on dates that meet the
criterion for having at least one observation at the given threshold.  The
distributions are presented as "violins" with the width of the violin
providing some insight into the population density at the given hour.
"""

from datetime import date

from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.util import month2months

PDICT = {
    "tmpf_above": "Temperature At or Above Threshold (F)",
    "tmpf_below": "Temperature Below Threshold (F)",
    "dwpf_above": "Dew Point At or Above Threshold (F)",
    "dwpf_below": "Dew Point Below Threshold (F)",
    "feel_above": "Feels Like Temperature At or Above Threshold (F)",
    "feel_below": "Feels Like Temperature Below Threshold (F)",
    "relh_above": "Relative Humidity At or Above Threshold (%)",
    "relh_below": "Relative Humidity Below Threshold (%)",
    "sknt_above": "Wind Speed At or Above Threshold (kts)",
    "sknt_below": "Wind Speed Below Threshold (kts)",
    "alti_above": "Pressure Altimeter At or Above Threshold (in)",
    "alti_below": "Pressure Altimeter Below Threshold (in)",
    "vsby_above": "Visibility At or Above Threshold (mi)",
    "vsby_below": "Visibility Below Threshold (mi)",
    "p01i_above": "Hourly Precipitation At or Above Threshold (in)",
    "p01i_below": "Hourly Precipitation Below Threshold (in)",
}
PDICT2 = {
    "tmpf": "Air Temperature (F)",
    "dwpf": "Dew Point (F)",
    "feel": "Feels Like Temperature (F)",
    "relh": "Relative Humidity (%)",
    "sknt": "Wind Speed (kts)",
    "alti": "Pressure Altimeter (in)",
    "vsby": "Visibility (mi)",
    "p01i": "Hourly Precipitation (in)",
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
        {
            "type": "select",
            "name": "var",
            "default": "tmpf",
            "label": "Variable to Summarize by Hour",
            "options": PDICT2,
        },
        dict(
            type="select",
            name="opt",
            default="tmpf_above",
            label="Daily Criterion with at least one ob?",
            options=PDICT,
        ),
        {
            "optional": True,
            "type": "date",
            "default": f"{date.today():%Y/%m/%d}",
            "label": "Plot observations for this calendar date",
            "name": "date",
        },
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="float",
            name="threshold",
            default="80",
            label="Threshold (F,knot,%,mile,inch):",
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["zstation"]
    threshold = ctx["threshold"]
    opt = ctx["opt"]
    dailyvar, dailydir = opt.split("_")
    hourlyvar = ctx["var"]
    if hourlyvar not in PDICT2:  # not possible, but alas
        raise NoDataFound(f"Invalid variable: {hourlyvar}")
    month = ctx["month"]
    mydate: date | None = ctx.get("date")

    months = month2months(month)

    params = {
        "tzname": ctx["_nt"].sts[station]["tzname"],
        "station": station,
        "threshold": threshold,
        "months": months,
    }

    mydate_obs = [[] for _ in range(24)]
    with get_sqlalchemy_conn("asos") as conn:
        res = conn.execute(
            sql_helper(
                """
            WITH events as (
                SELECT distinct date(valid at time zone :tzname) from alldata
                WHERE station = :station and
                extract(month from valid at time zone :tzname) = ANY(:months)
                and {dailyvar} {mydir} :threshold
            )
        SELECT valid at time zone :tzname + '10 minutes'::interval, {hourlyvar}
        from alldata a, events e where
        a.station = :station and
    (date((a.valid + '10 minutes'::interval) at time zone :tzname) = e.date)
        and report_type = 3 and {hourlyvar} is not null
        """,
                dailyvar=dailyvar,
                mydir=">=" if dailydir == "above" else "<",
                hourlyvar=hourlyvar,
            ),
            params,
        )
        data = [[] for _ in range(24)]
        if res.rowcount == 0:
            raise NoDataFound("Failed to find any data for station.")
        for row in res:
            data[row[0].hour].append(row[1])
            if mydate and row[0].date() == mydate:
                mydate_obs[row[0].hour].append(row[1])

    title = (
        f"{ctx['_sname']} :: Hourly {PDICT2[hourlyvar]} "
        f"Distributions over ({month.capitalize()})"
    )
    subtitle = f"On Dates with at least one ob {PDICT[opt]} {threshold:.2f}"
    fig, ax = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    v1 = ax.violinplot(data, showextrema=True, showmeans=True, widths=0.7)
    for lbl in ["cmins", "cmeans", "cmaxes"]:
        v1[lbl].set_color("r")

    ax.grid(True)
    ax.set_ylabel(PDICT2[hourlyvar])
    ax.set_xlabel(
        f"Local Hour for Timezone: {ctx['_nt'].sts[station]['tzname']}"
    )
    ax.set_xticks(range(1, 25, 3))
    ax.set_xticklabels("Mid,3 AM,6 AM,9 AM,Noon,3 PM,6 PM,9 PM".split(","))
    labeled = False
    for hr, obs in enumerate(mydate_obs, start=1):
        if obs:
            ax.scatter(
                [hr] * len(obs),
                obs,
                marker="o",
                color="k",
                zorder=10,
                label=None if labeled else f"{mydate:%Y-%m-%d}",
            )
            labeled = True
    if labeled:
        ax.legend(loc="upper right", fontsize=10, framealpha=0.8)
    return fig
