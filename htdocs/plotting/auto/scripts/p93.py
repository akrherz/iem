"""hourly histogram"""
import datetime
from collections import OrderedDict

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound
from metpy.units import units
from metpy.calc import heat_index, windchill, relative_humidity_from_dewpoint


PDICT = {
    "yes": "Yes, Include only Year to Date period each year",
    "no": "No, Include all available data for each year",
}
VDICT = OrderedDict(
    [
        ("tmpf", "Air Temperature"),
        ("dwpf", "Dew Point Temperature"),
        ("heatindex", "Heat Index"),
        ("windchill", "Wind Chill Index"),
    ]
)
LEVELS = {
    "tmpf": np.arange(85, 115),
    "dwpf": np.arange(60, 85),
    "heatindex": np.arange(80, 121),
    "windchill": np.arange(-50, 1),
}
OPTDICT = {
    "no": "No, only include times when heatindex/windchill is additive",
    "yes": "Yes, include all observations",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """Caution: This plot takes a bit of time to
    generate. This plot displays a histogram of hourly heat index
    values or temperature or dew point or wind chill.
    The connecting lines between the dots are to help readability. In the
    case of wind chill, the year shown is for the winter season actual year
    with December contained within.

    <p>This form provides an option for the case of wind chill and heat index
    to only include cases that are additive.  What this means is to only
    include observations where the wind chill temperature is colder than the
    air temperature or when the heat index temperature is warmer than the
    air temperature.</p>

    <p>This application only considers one observation per hour.  In the case
    of multiple observations within an hour, a simple average of the found
    values is used.  In the future, the hope is to limit the considered data
    to the "synoptic" observation at the top of the hour, but we are not there
    yet.</p>

    <p><strong>Change made 29 Aug 2018</strong>: The algorithm used here was
    updated to use greater than or equal to the given threshold.  In the case
    of wind chill, it is less than or equal to.</p>
    """
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="year",
            minvalue=1973,
            default=1973,
            name="syear",
            label="Start year (if data available) for plot:",
        ),
        dict(
            type="year",
            minvalue=1973,
            default=datetime.date.today().year,
            name="eyear",
            label="End year (inclusive, if data available) for plot:",
        ),
        dict(
            type="year",
            minvalue=1973,
            default=datetime.date.today().year,
            name="year",
            label="Year to Highlight:",
        ),
        dict(
            type="select",
            options=VDICT,
            name="var",
            default="heatindex",
            label="Select variable to plot:",
        ),
        dict(
            type="select",
            options=PDICT,
            name="ytd",
            default="no",
            label="Include Only Year to Date Data?",
        ),
        dict(
            type="select",
            options=OPTDICT,
            name="inc",
            default="no",
            label=(
                "Include cases where windchill or heatindex " "is not additive"
            ),
        ),
    ]
    return desc


def get_doylimit(ytd, varname):
    """Get the SQL limiter"""
    if ytd == "no":
        return ""
    if varname != "windchill":
        return "and extract(doy from valid) < extract(doy from 'TODAY'::date)"
    today = datetime.date.today()
    if today.month > 7:
        return "and extract(doy from valid) < extract(doy from 'TODAY'::date)"

    return (
        "and (extract(doy from valid) < extract(doy from 'TODAY'::date) "
        "or extract(month from valid) > 6)"
    )


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("asos")

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    highlightyear = ctx["year"]
    sdate = datetime.date(ctx["syear"], 1, 1)
    edate = datetime.date(ctx["eyear"] + 1, 1, 1)
    ytd = ctx["ytd"]
    varname = ctx["var"]
    inc = ctx["inc"]
    doylimiter = get_doylimit(ytd, varname)
    tmpflimit = "and tmpf >= 50" if varname != "windchill" else "and tmpf < 50"
    if varname not in ["windchill", "heatindex"]:
        tmpflimit = ""

    df = read_sql(
        "SELECT to_char(valid, 'YYYYmmddHH24') as d, avg(tmpf)::int as tmpf, "
        "avg(dwpf)::int as dwpf, avg(coalesce(sknt, 0)) as sknt "
        f"from alldata WHERE station = %s {tmpflimit} "
        "and dwpf <= tmpf and valid > %s and valid < %s and report_type = 2 "
        f"{doylimiter} GROUP by d",
        pgconn,
        params=(station, sdate, edate),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["year"] = df["d"].apply(lambda x: int(x[:4]))

    df2 = df
    title2 = VDICT[varname]
    compop = np.greater_equal
    inctitle = ""
    if varname == "heatindex":
        df["heatindex"] = (
            heat_index(
                df["tmpf"].values * units("degF"),
                relative_humidity_from_dewpoint(
                    df["tmpf"].values * units("degF"),
                    df["dwpf"].values * units("degF"),
                ),
            )
            .to(units("degF"))
            .m
        )
        inctitle = " [All Obs Included]"
        if inc == "no":
            df2 = df[df["heatindex"] > df["tmpf"]]
            inctitle = " [Only Additive]"
        else:
            df2 = df
        maxval = int(df2["heatindex"].max() + 1)
        LEVELS[varname] = np.arange(80, maxval)
    elif varname == "windchill":
        compop = np.less_equal
        df["year"] = df["d"].apply(
            lambda x: (int(x[:4]) - 1) if int(x[4:6]) < 7 else int(x[:4])
        )
        df["windchill"] = (
            windchill(
                df["tmpf"].values * units("degF"),
                df["sknt"].values * units("knot"),
            )
            .to(units("degF"))
            .m
        )
        inctitle = " [All Obs Included]"
        if inc == "no":
            df2 = df[df["windchill"] < df["tmpf"]]
            inctitle = " [Only Additive]"
        else:
            df2 = df
        minval = int(df2["windchill"].min() - 1)
        LEVELS[varname] = np.arange(minval, minval + 51)
    else:
        maxval = int(df2[varname].max() + 1)
        LEVELS[varname] = np.arange(maxval - 31, maxval)

    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("Unknown station metadata.")
    minyear = df["year"].min()
    maxyear = df["year"].max()
    years = float((maxyear - minyear) + 1)
    x = []
    y = []
    y2 = []
    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_axes([0.1, 0.1, 0.6, 0.8])
    yloc = 1.0
    xloc = 1.13
    yrlabel = (
        "%s" % (highlightyear,)
        if varname != "windchill"
        else "%s-%s" % (highlightyear, highlightyear + 1)
    )
    ax.text(
        xloc + 0.08, yloc + 0.04, "Avg:", transform=ax.transAxes, color="b"
    )
    ax.text(
        xloc + 0.21, yloc + 0.04, yrlabel, transform=ax.transAxes, color="r"
    )
    df3 = df2[df2["year"] == highlightyear]
    for level in LEVELS[varname]:
        x.append(level)
        y.append(len(df2[compop(df2[varname], level)]) / years)
        y2.append(len(df3[compop(df3[varname], level)]))
        if level % 2 == 0:
            ax.text(xloc, yloc, "%s" % (level,), transform=ax.transAxes)
            ax.text(
                xloc + 0.08,
                yloc,
                "%.1f" % (y[-1],),
                transform=ax.transAxes,
                color="b",
            )
            ax.text(
                xloc + 0.21,
                yloc,
                "%.0f" % (y2[-1],),
                transform=ax.transAxes,
                color="r",
            )
            yloc -= 0.04
    ax.text(xloc, yloc, "n=%s" % (len(df2.index),), transform=ax.transAxes)
    for x0, y0, y02 in zip(x, y, y2):
        ax.plot([x0, x0], [y0, y02], color="k")
    rdf = pd.DataFrame({"level": x, "avg": y, "d%s" % (highlightyear,): y2})
    x = np.array(x, dtype=np.float64)
    ax.scatter(x, y, color="b", label="Avg")
    ax.scatter(x, y2, color="r", label=yrlabel)
    ax.grid(True)
    ymax = int(max([max(y), max(y2)]))
    ax.set_xlim(x[0] - 0.5, x[-1] + 0.5)
    dy = 24 * (int(ymax / 240) + 1)
    ax.set_yticks(range(0, ymax, dy))
    ax.set_ylim(-0.5, ymax + 5)
    ax2 = ax.twinx()
    ax2.set_ylim(-0.5, ymax + 5)
    ax2.set_yticks(range(0, ymax, dy))
    ax2.set_yticklabels(["%.0f" % (s,) for s in np.arange(0, ymax, dy) / 24])
    ax2.set_ylabel("Expressed in 24 Hour Days")
    ax.set_ylabel("Hours Per Year")
    ax.set_xlabel(r"%s $^\circ$F" % (VDICT[varname],))
    title = "till %s" % (datetime.date.today().strftime("%-d %b"),)
    title = "Entire Year" if ytd == "no" else title
    ax.set_title(
        ("[%s] %s %s-%s\n" "%s Histogram (%s)%s")
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            minyear,
            maxyear,
            title2,
            title,
            inctitle,
        )
    )
    ax.legend(loc="best", scatterpoints=1)
    return fig, rdf


if __name__ == "__main__":
    plotter(
        dict(
            ytd="yes", network="IA_ASOS", zstation="AMW", var="tmpf", inc="yes"
        )
    )
