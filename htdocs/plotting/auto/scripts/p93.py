"""hourly histogram"""
import datetime

import numpy as np
import pandas as pd
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound


PDICT = {
    "yes": "Yes, Include only Year to Date period each year",
    "no": "No, Include all available data for each year",
}
VDICT = {
    "tmpf": "Air Temperature",
    "dwpf": "Dew Point Temperature",
    "heatindex": "Heat Index",
    "windchill": "Wind Chill Index",
    "gust": "Wind Gust",
}
LEVELS = {
    "tmpf": np.arange(85, 115),
    "dwpf": np.arange(60, 85),
    "heatindex": np.arange(80, 121),
    "windchill": np.arange(-50, 1),
    "gust": np.arange(30, 71),
}
OPTDICT = {
    "no": "No, only include times when heatindex/windchill is additive",
    "yes": "Yes, include all observations",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
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
    if datetime.date.today().month > 7:
        res = "and extract(doy from valid) < extract(doy from 'TODAY'::date) "
        if varname == "windchill":
            res += "and extract(month from valid) > 6"
        return res

    return (
        "and (extract(doy from valid) < extract(doy from 'TODAY'::date) "
        "or extract(month from valid) > 6)"
    )


def plotter(fdict):
    """Go"""
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
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            f"""
            SELECT valid at time zone 'UTC' as valid,
            tmpf::int as tmpf, gust * 1.15 as gust,
            dwpf::int as dwpf, feel
            from alldata WHERE station = %s {tmpflimit}
            and dwpf <= tmpf and valid > %s and valid < %s
            and report_type = 3 {doylimiter}""",
            conn,
            params=(station, sdate, edate),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("Unknown station metadata.")
    df["year"] = df["valid"].dt.year

    df2 = df
    title2 = VDICT[varname]
    compop = np.greater_equal
    inctitle = ""
    if varname == "heatindex":
        df[varname] = df["feel"]
        inctitle = " [All Obs Included]"
        if inc == "no":
            df2 = df[df["feel"] > df["tmpf"]]
            inctitle = " [Only Additive]"
        else:
            df2 = df
        maxval = int(df2["feel"].max() + 1)
        LEVELS[varname] = np.arange(80, maxval)
    elif varname == "windchill":
        df[varname] = df["feel"]
        compop = np.less_equal
        df["year"] = df["valid"].apply(
            lambda x: (x.year - 1) if x.month < 7 else x.year
        )
        inctitle = " [All Obs Included]"
        if inc == "no":
            df2 = df[df["feel"] < df["tmpf"]]
            inctitle = " [Only Additive]"
        else:
            df2 = df
        minval = int(df2["feel"].min() - 1)
        LEVELS[varname] = np.arange(minval, minval + 51)
    elif varname == "gust":
        pass
    else:
        maxval = int(df2[varname].max() + 1)
        LEVELS[varname] = np.arange(maxval - 31, maxval)

    minyear = df["year"].min()
    maxyear = df["year"].max()
    years = float((maxyear - minyear) + 1)
    x = []
    y = []
    y2 = []
    title = f"till {datetime.date.today():%-d %b}"
    title = "Entire Year" if ytd == "no" else title
    title = (
        f"{ctx['_sname']} ({minyear}-{maxyear})\n"
        f"{title2} Histogram ({title}){inctitle}"
    )
    fig, ax = figure_axes(title=title, apctx=ctx)
    ax.set_position([0.06, 0.1, 0.64, 0.8])
    yloc = 1.0
    xloc = 1.13
    yrlabel = (
        f"{highlightyear}"
        if varname != "windchill"
        else f"{highlightyear}-{highlightyear + 1}"
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
        y.append(len(df2[compop(df2[varname], level)].index) / years)
        y2.append(len(df3[compop(df3[varname], level)].index))

        if level % 2 == 0:
            ax.text(xloc, yloc, f"{level}", transform=ax.transAxes)
            ax.text(
                xloc + 0.08,
                yloc,
                f"{y[-1]:.1f}",
                transform=ax.transAxes,
                color="b",
            )
            ax.text(
                xloc + 0.21,
                yloc,
                f"{y2[-1]:.0f}",
                transform=ax.transAxes,
                color="r",
            )
            yloc -= 0.04
    ax.text(xloc, yloc, f"n={len(df2.index)}", transform=ax.transAxes)
    for x0, y0, y02 in zip(x, y, y2):
        ax.plot([x0, x0], [y0, y02], color="k")
    rdf = pd.DataFrame({"level": x, "avg": y, f"d{highlightyear}": y2})
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
    ax2.set_yticklabels([f"{s:.0f}" for s in np.arange(0, ymax, dy) / 24])
    ax2.set_ylabel("Expressed in 24 Hour Days")
    ax.set_ylabel("Hours Per Year")
    unit = r"$^\circ$F" if varname != "gust" else "MPH"
    ax.set_xlabel(f"{VDICT[varname]} {unit}")
    ax.legend(loc=(2 if varname == "windchill" else 1), scatterpoints=1)
    return fig, rdf


if __name__ == "__main__":
    plotter(
        dict(
            ytd="yes", network="UT_ASOS", zstation="SGU", var="dwpf", inc="yes"
        )
    )
