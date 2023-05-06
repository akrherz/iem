"""last spring temp"""
import datetime

import matplotlib.dates as mdates
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["report"] = True
    desc[
        "description"
    ] = """This chart presents the accumulated frequency of
    having the last spring temperature at or below a given threshold."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(type="int", name="t1", default=32, label="First Threshold (F)"),
        dict(type="int", name="t2", default=28, label="Second Threshold (F)"),
        dict(type="int", name="t3", default=26, label="Third Threshold (F)"),
        dict(type="int", name="t4", default=22, label="Fourth Threshold (F)"),
        dict(
            type="year",
            name="syear",
            min=1880,
            label="Potential (if data exists) minimum year",
            default=1880,
        ),
        dict(
            type="year",
            name="eyear",
            min=1880,
            label="Potential (if data exists) exclusive maximum year",
            default=datetime.date.today().year,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    thresholds = [ctx["t1"], ctx["t2"], ctx["t3"], ctx["t4"]]

    df = pd.DataFrame(
        {
            "dates": pd.date_range("2000/01/29", "2000/06/30"),
            "%scnts" % (thresholds[0],): 0,
            "%scnts" % (thresholds[1],): 0,
            "%scnts" % (thresholds[2],): 0,
            "%scnts" % (thresholds[3],): 0,
        },
        index=range(29, 183),
    )
    df.index.name = "doy"

    for base in thresholds:
        # Query Last doy for each year in archive
        with get_sqlalchemy_conn("coop") as conn:
            df2 = pd.read_sql(
                """
                select year,
                max(case when low <= %s then extract(doy from day)
                    else 0 end) as doy from alldata
                WHERE month < 7 and station = %s and year > %s and year < %s
                GROUP by year
            """,
                conn,
                params=(base, station, ctx["syear"], ctx["eyear"]),
                index_col=None,
            )
        for _, row in df2.iterrows():
            if row["doy"] == 0:
                continue
            df.loc[0 : row["doy"], "%scnts" % (base,)] += 1
        df["%sfreq" % (base,)] = (
            df["%scnts" % (base,)] / len(df2.index) * 100.0
        )

    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("No metadata found.")
    res = """\
# IEM Climodat https://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# Low Temperature exceedence probabilities
# (On a certain date, what is the chance a temperature below a certain
# threshold would be observed again that spring season)
 DOY Date    <%s  <%s  <%s  <%s
""" % (
        datetime.date.today().strftime("%d %b %Y"),
        max([bs, datetime.date(ctx["syear"], 1, 1)]),
        min([datetime.date.today(), datetime.date(ctx["eyear"] - 1, 12, 31)]),
        station,
        ctx["_nt"].sts[station]["name"],
        thresholds[0] + 1,
        thresholds[1] + 1,
        thresholds[2] + 1,
        thresholds[3] + 1,
    )
    fcols = ["%sfreq" % (s,) for s in thresholds]
    mindate = None
    for doy, row in df.iterrows():
        if doy % 2 != 0:
            continue
        if row[fcols[3]] < 100 and mindate is None:
            mindate = row["dates"] - datetime.timedelta(days=5)
        res += (" %3s %s  %3i  %3i  %3i  %3i\n") % (
            row["dates"].strftime("%-j"),
            row["dates"].strftime("%b %d"),
            row[fcols[0]],
            row[fcols[1]],
            row[fcols[2]],
            row[fcols[3]],
        )

    title = "Frequency of Last Spring Temperature"
    subtitle = "%s %s (%s-%s)" % (
        station,
        ctx["_nt"].sts[station]["name"],
        max([bs, datetime.date(ctx["syear"], 1, 1)]),
        min([datetime.date.today(), datetime.date(ctx["eyear"] - 1, 12, 31)]),
    )
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    for base in thresholds:
        ax.plot(
            df["dates"].values,
            df[f"{base}freq"],
            label=f"{base}",
            lw=2,
        )

    ax.legend(loc="best")
    ax.set_xlim(mindate)
    ax.xaxis.set_major_locator(mdates.DayLocator([1, 7, 14, 21]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%b"))
    ax.grid(True)
    df = df.reset_index()
    return fig, df, res


if __name__ == "__main__":
    plotter({})
