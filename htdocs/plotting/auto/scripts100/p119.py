"""Frequency of first fall low"""
import datetime

from pandas.io.sql import read_sql
import pandas as pd
import matplotlib.dates as mdates
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {"low": "Low Temperature", "high": "High Temperature"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = dict()
    desc["data"] = True
    desc["report"] = True
    desc[
        "description"
    ] = """This chart presents the accumulated frequency of
    having the first fall temperature at or below a given threshold."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            options=PDICT,
            name="var",
            default="low",
            label="Select variable to summarize:",
        ),
        dict(type="int", name="t1", default=32, label="First Threshold (F)"),
        dict(type="int", name="t2", default=28, label="Second Threshold (F)"),
        dict(type="int", name="t3", default=26, label="Third Threshold (F)"),
        dict(type="int", name="t4", default=22, label="Fourth Threshold (F)"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    thresholds = [ctx["t1"], ctx["t2"], ctx["t3"], ctx["t4"]]

    table = "alldata_%s" % (station[:2],)
    # Load up dict of dates..

    sz = 214 + 304
    df = pd.DataFrame(
        {
            "dates": pd.date_range("2000/08/01", "2001/05/31"),
            "%scnts" % (thresholds[0],): 0,
            "%scnts" % (thresholds[1],): 0,
            "%scnts" % (thresholds[2],): 0,
            "%scnts" % (thresholds[3],): 0,
        },
        index=range(214, sz),
    )
    df.index.name = "doy"

    for base in thresholds:
        # Find first dates by winter season
        df2 = read_sql(
            f"""
            select
            case when month > 7 then year + 1 else year end as winter,
            min(case when {ctx["var"]} <= %s
            then day else '2099-01-01'::date end) as mindate from {table}
            WHERE month not in (6, 7) and station = %s and year < %s
            GROUP by winter
        """,
            pgconn,
            params=(base, station, datetime.date.today().year),
            index_col=None,
        )
        for _, row in df2.iterrows():
            if row["mindate"].year == 2099:
                continue
            jan1 = datetime.date(row["winter"] - 1, 1, 1)
            doy = (row["mindate"] - jan1).days
            df.loc[doy:sz, "%scnts" % (base,)] += 1
        df[f"{base}freq"] = df[f"{base}cnts"] / len(df2.index) * 100.0

    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("Unknown metadata")
    res = """\
# IEM Climodat https://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# %s exceedence probabilities
# (On a certain date, what is the chance a temperature below a certain
# threshold would have been observed once already during the fall of that year)
 DOY Date    <%s  <%s  <%s  <%s
""" % (
        datetime.date.today().strftime("%d %b %Y"),
        bs.date(),
        datetime.date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
        PDICT[ctx["var"]],
        thresholds[0] + 1,
        thresholds[1] + 1,
        thresholds[2] + 1,
        thresholds[3] + 1,
    )
    fcols = ["%sfreq" % (s,) for s in thresholds]
    mindate = None
    maxdate = None
    for doy, row in df.iterrows():
        if doy % 2 != 0:
            continue
        if row[fcols[3]] >= 100:
            if maxdate is None:
                maxdate = row["dates"] + datetime.timedelta(days=5)
            continue
        if row[fcols[0]] > 0 and mindate is None:
            mindate = row["dates"] - datetime.timedelta(days=5)
        res += (" %3s %s  %3i  %3i  %3i  %3i\n") % (
            row["dates"].strftime("%-j"),
            row["dates"].strftime("%b %d"),
            row[fcols[0]],
            row[fcols[1]],
            row[fcols[2]],
            row[fcols[3]],
        )
    if maxdate is None:
        maxdate = datetime.datetime(2001, 6, 1)

    title = (
        "Frequency of First Fall %s At or Below Threshold\n%s %s (%s-%s)"
    ) % (
        PDICT[ctx["var"]],
        station,
        ctx["_nt"].sts[station]["name"],
        bs.year,
        datetime.date.today().year,
    )
    (fig, ax) = figure_axes(title=title)
    for base in thresholds:
        ax.plot(
            df["dates"].values,
            df["%sfreq" % (base,)],
            label="%s" % (base,),
            lw=2,
        )

    ax.legend(loc="best")
    ax.set_xlim(mindate, maxdate)
    days = (maxdate - mindate).days
    dl = [1] if days > 120 else [1, 7, 14, 21]
    ax.xaxis.set_major_locator(mdates.DayLocator(dl))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%b"))
    ax.grid(True)
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.set_ylabel("Accumulated to Date Frequency [%]")
    df = df.reset_index()
    return fig, df, res


if __name__ == "__main__":
    plotter({"var": "high", "t4": 0})
