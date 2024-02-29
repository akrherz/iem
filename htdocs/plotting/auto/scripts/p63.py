"""
This chart plots the number of daily maximum
high temperatures, minimum low temperatures and precipitation records
set by year.  Ties are not included.  The algorithm sets the records based
on the first year of data and then iterates over each sequential year
and sets the new daily records.  A general model of the number of new
records to be set each year would be 365 / (number of years).  So you would
expect to set 365 records the first year, 183 the second, and so on...
"""

import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_dbconnc


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        )
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]

    sts = ctx["_nt"].sts[station]["archive_begin"]
    if sts is None:
        raise NoDataFound("Station metadata unknown.")
    pgconn, cursor = get_dbconnc("coop")
    syear = sts.year if sts.month == 1 and sts.day == 1 else (sts.year + 1)
    syear = max(syear, 1893)
    eyear = datetime.datetime.now().year

    cursor.execute(
        """
        SELECT sday, year, high, low, precip, day from alldata
        where station = %s and sday != '0229'
        and year >= %s and high is not null and low is not null
        and precip is not null ORDER by day ASC
    """,
        (station, syear),
    )

    hrecords = {}
    hyears = [0] * (eyear - syear)
    lrecords = {}
    lyears = [0] * (eyear - syear)
    precords = {}
    pyears = [0] * (eyear - syear)
    expect = [0] * (eyear - syear)

    # hstraight = 0
    for row in cursor:
        sday = row["sday"]
        year = row["year"]
        high = row["high"]
        low = row["low"]
        precip = row["precip"]
        if year == syear:
            hrecords[sday] = high
            lrecords[sday] = low
            precords[sday] = precip
            continue
        if precip > precords[sday]:
            precords[sday] = row["precip"]
            pyears[year - syear - 1] += 1
        if high > hrecords[sday]:
            hrecords[sday] = row["high"]
            hyears[year - syear - 1] += 1
        if low < lrecords[sday]:
            lrecords[sday] = low
            lyears[year - syear - 1] += 1
    pgconn.close()
    years = range(syear + 1, eyear + 1)
    for i, year in enumerate(years):
        expect[i] = 365.0 / float(year - syear + 1)

    df = pd.DataFrame(
        dict(
            expected=pd.Series(expect),
            highs=pd.Series(hyears),
            lows=pd.Series(lyears),
            precip=pd.Series(pyears),
            year=years,
        )
    )
    title = (
        f"{ctx['_sname']}\n"
        "Daily Records Set Per Year "
        f"{syear} sets record then accumulate ({syear + 1}-{eyear})\n"
        "events/year value is long term average, total events / "
        f"{(eyear - syear - 1):.0f} years"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(3, 1, sharex=True, sharey=True)
    rects = ax[0].bar(years, hyears, facecolor="b", edgecolor="b")
    for i, rect in enumerate(rects):
        if rect.get_height() > expect[i]:
            rect.set_facecolor("r")
            rect.set_edgecolor("r")
    ax[0].plot(years, expect, color="black", label="$365/n$")
    ax[0].set_ylim(0, 50)
    ax[0].set_xlim(syear, eyear + 1)
    ax[0].grid(True)
    ax[0].legend()
    ax[0].set_ylabel("Records set per year")

    rate = sum(hyears) / float(len(hyears))
    ax[0].text(
        eyear - 70,
        32,
        f"Max High Temperature, {rate:.1f} events/year",
        bbox=dict(color="white"),
    )

    rects = ax[1].bar(years, lyears, facecolor="r", edgecolor="r")
    for i, rect in enumerate(rects):
        if rect.get_height() > expect[i]:
            rect.set_facecolor("b")
            rect.set_edgecolor("b")
    ax[1].plot(years, expect, color="black", label="$365/n$")
    ax[1].grid(True)
    ax[1].legend()
    ax[1].set_ylabel("Records set per year")
    rate = sum(lyears) / float(len(lyears))
    ax[1].text(
        eyear - 70,
        32,
        f"Min Low Temperature, {rate:.1f} events/year",
        bbox=dict(color="white"),
    )

    rects = ax[2].bar(years, pyears, facecolor="r", edgecolor="r")
    for i, rect in enumerate(rects):
        if rect.get_height() > expect[i]:
            rect.set_facecolor("b")
            rect.set_edgecolor("b")
    ax[2].plot(years, expect, color="black", label="$365/n$")
    ax[2].grid(True)
    ax[2].legend()
    ax[2].set_ylabel("Records set per year")
    rate = sum(pyears) / float(len(pyears))
    ax[2].text(
        eyear - 50,
        32,
        f"Precipitation, {rate:.1f} events/year",
        bbox=dict(color="white"),
    )

    return fig, df


if __name__ == "__main__":
    plotter({})
