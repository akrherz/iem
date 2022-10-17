"""warmest 91 days"""
import datetime

import psycopg2.extras
import numpy as np
import pandas as pd
from scipy import stats
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


PDICT = {"end_summer": "End of Summer", "start_summer": "Start of Summer"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This chart presents the start or end date of the
    warmest 91 day period each year.
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="which",
            default="end_summer",
            label="Which value to plot:",
            options=PDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    which = ctx["which"]
    station = ctx["station"]

    cursor.execute(
        f"""
    select year, extract(doy from day) as d from
        (select day, year, rank() OVER (PARTITION by year ORDER by avg DESC)
        from
            (select day, year, avg((high+low)/2.) OVER
            (ORDER by day ASC rows 91 preceding) from alldata_{station[:2]}
            where station = %s and day > '1893-01-01') as foo)
            as foo2 where rank = 1
            ORDER by year ASC
    """,
        (station,),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found.")
    years = []
    maxsday = []
    today = datetime.date.today()
    delta = 0 if which == "end_summer" else 91
    for row in cursor:
        if row["year"] == today.year and row["d"] < 270:
            continue
        maxsday.append(int(row["d"]) - delta)
        years.append(row["year"])

    df = pd.DataFrame(dict(year=pd.Series(years), doy=pd.Series(maxsday)))
    maxsday = np.array(maxsday)
    t1 = "End" if delta == 0 else "Start"
    title = (
        f"{ctx['_sname']} :: {PDICT.get(which)}\n"
        f"{t1} Date of Warmest (Avg Temp) 91 Day Period"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.scatter(years, maxsday)
    ax.grid(True)
    ax.set_ylabel(f"{t1} Date")

    yticks = []
    yticklabels = []
    for i in np.arange(min(maxsday) - 5, max(maxsday) + 5, 1):
        ts = datetime.datetime(2000, 1, 1) + datetime.timedelta(days=int(i))
        if ts.day in [1, 8, 15, 22, 29]:
            yticks.append(i)
            yticklabels.append(ts.strftime("%-d %b"))
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)

    h_slope, intercept, r_value, _, _ = stats.linregress(years, maxsday)
    ax.plot(years, h_slope * np.array(years) + intercept, lw=2, color="r")

    avgd = datetime.datetime(2000, 1, 1) + datetime.timedelta(
        days=int(np.average(maxsday))
    )
    ax.text(
        0.1,
        0.03,
        "Avg Date: %s, slope: %.2f days/century, R$^2$=%.2f"
        % (avgd.strftime("%-d %b"), h_slope * 100.0, r_value**2),
        transform=ax.transAxes,
        va="bottom",
    )
    ax.set_xlim(min(years) - 1, max(years) + 1)
    ax.set_ylim(min(maxsday) - 5, max(maxsday) + 5)

    return fig, df


if __name__ == "__main__":
    plotter({})
