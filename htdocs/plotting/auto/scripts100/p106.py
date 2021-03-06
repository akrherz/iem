"""hourly histogram on days"""
import datetime
from collections import OrderedDict

import psycopg2.extras
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {
    "tmpf_above": "Temperature At or Above Threshold (F)",
    "tmpf_below": "Temperature Below Threshold (F)",
}

MDICT = OrderedDict(
    [
        ("all", "No Month/Time Limit"),
        ("spring", "Spring (MAM)"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("jan", "January"),
        ("feb", "February"),
        ("mar", "March"),
        ("apr", "April"),
        ("may", "May"),
        ("jun", "June"),
        ("jul", "July"),
        ("aug", "August"),
        ("sep", "September"),
        ("oct", "October"),
        ("nov", "November"),
        ("dec", "December"),
    ]
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc[
        "description"
    ] = """
    This plot displays hourly temperature distributions on dates having at
    least one hourly observation meeting the given requirement.  The
    distributions are presented as "violins" with the width of the violin
    providing some insight into the population density at the given
    temperature.
    """
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


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    threshold = ctx["threshold"]
    opt = ctx["opt"]
    month = ctx["month"]

    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    if opt == "tmpf_above":
        limiter = "round(tmpf::numeric,0) >= %s" % (threshold,)
    else:
        limiter = "round(tmpf::numeric,0) < %s" % (threshold,)

    cursor.execute(
        f"""
        WITH obs as (
            SELECT valid, tmpf from alldata WHERE
            station = %s and extract(month from valid) in %s and tmpf > -80
        ),
        events as (
            SELECT distinct date(valid at time zone %s) from obs
            WHERE {limiter})
     SELECT valid at time zone %s + '10 minutes'::interval, tmpf
     from obs a JOIN events e on
     (date(a.valid at time zone %s) = e.date)
    """,
        (
            station,
            tuple(months),
            ctx["_nt"].sts[station]["tzname"],
            ctx["_nt"].sts[station]["tzname"],
            ctx["_nt"].sts[station]["tzname"],
        ),
    )
    data = []
    for _ in range(24):
        data.append([])
    for row in cursor:
        data[row[0].hour].append(row[1])

    title = "%s [%s] Hourly Temp Distributions over (%s)" % (
        ctx["_nt"].sts[station]["name"],
        station,
        month.capitalize(),
    )
    subtitle = "On Dates with at least one temperature ob %s %.0f" % (
        PDICT[opt],
        threshold,
    )
    fig, ax = figure_axes(title=title, subtitle=subtitle)
    v1 = ax.violinplot(data, showextrema=True, showmeans=True, widths=0.7)
    for lbl in ["cmins", "cmeans", "cmaxes"]:
        v1[lbl].set_color("r")

    ax.grid(True)
    ax.set_ylabel(r"Temperature $^\circ$F")
    ax.set_xlabel(
        "Local Hour for Timezone: %s" % (ctx["_nt"].sts[station]["tzname"],)
    )
    ax.set_xticks(range(1, 25, 3))
    ax.set_xticklabels("Mid,3 AM,6 AM,9 AM,Noon,3 PM,6 PM,9 PM".split(","))
    return fig


if __name__ == "__main__":
    plotter(dict())
