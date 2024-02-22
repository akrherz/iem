"""
This reports presents simple monthy and yearly
summary statistics.  The <i>WYEAR</i> column denotes the 'Water Year'
total, which is defined for the period between 1 Oct and 30 Sep. For
example, the 2009 <i>WYEAR</i> value represents the period between
1 Oct 2008 and 30 Sep 2009, the 2009 water year.
"""
import calendar
import datetime

import pandas as pd
import seaborn as sns
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

PDICT = {
    "precip": "Total Precipitation",
    "snow": "Total Snowfall",
    "avg_high": "Average High Temperature",
    "avg_low": "Average Low Temperature",
    "avg_temp": "Average Monthly Temperature",
}
FMT = {
    "precip": ".2f",
    "snow": ".1f",
    "avg_high": ".1f",
    "avg_low": ".1f",
    "avg_temp": ".1f",
}

LABELS = {
    "precip": "Monthly Liquid Precip Totals [inches] (snow is melted)",
    "snow": "Monthly Snow Fall [inches]",
    "avg_high": "Monthly Average High Temperatures [F]",
    "avg_low": "Monthly Average Low Temperatures [F]",
    "avg_temp": "Monthly Average Temperatures [F] (High + low)/2",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "report": True}
    y20 = datetime.date.today().year - 19
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
            name="var",
            default="precip",
            label="Select variable:",
            options=PDICT,
        ),
        {
            "type": "year",
            "name": "syear",
            "default": y20,
            "label": "For plotting, year to start 20 years of plot",
        },
        dict(type="cmap", name="cmap", default="plasma", label="Color Ramp:"),
    ]
    return desc


def myformat(val, precision):
    """Nice"""
    if val is None:
        return " ****"
    fmt = f"%5.{precision}f"
    return fmt % val


def p(df, year, month, varname, precision):
    """Lazy request of data"""
    try:
        val = df.at[(year, month), varname]
    except Exception:
        return " ****"
    if pd.isna(val):
        return " ****"
    fmt = f"%5.{precision}f"
    return fmt % val


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["station"]
    varname = ctx["var"]

    with get_sqlalchemy_conn("coop") as conn:
        # Prevent trace values from accumulating
        df = pd.read_sql(
            """
            SELECT year, month,
            case when month in (10, 11, 12) then year + 1 else year end
            as water_year,
            round(sum(precip)::numeric, 2) as precip,
            round(sum(snow)::numeric, 2) as snow,
            avg(high) as avg_high, avg(low) as avg_low,
            avg((high+low)/2.) as avg_temp, max(day) as max_day from
            alldata WHERE station = %s
            GROUP by year, water_year, month ORDER by year ASC, month ASC
        """,
            conn,
            params=(station,),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        f"# Report Generated: {datetime.date.today():%d %b %Y}\n"
        f"# Climate Record: {ctx['_nt'].sts[station]['archive_begin']} "
        f"-> {df['max_day'].max()}, "
        "WYEAR column is Water Year Oct 1 - Sep 30\n"
        f"# Site Information: {ctx['_sname']}\n"
        "# Contact Information: "
        "Daryl Herzmann akrherz@iastate.edu 515.294.5978\n"
        f"# {LABELS[varname]}\n"
        "YEAR   JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   "
        "OCT   NOV   DEC   ANN WYEAR\n"
    )

    years = df["year"].unique()
    years.sort()
    grouped = df.set_index(["year", "month"])
    yrsum = df.groupby("year")[varname].sum()
    wyrsum = df.groupby("water_year")[varname].sum()
    yrmean = df.groupby("year")[varname].mean()
    wyrmean = df.groupby("water_year")[varname].mean()

    prec = 2 if varname == "precip" else 0
    if varname == "snow":
        prec = 1
    for year in years:
        yrtot = yrsum[year]
        wyrtot = wyrsum.get(year, 0)
        if varname not in ["precip", "snow"]:
            yrtot = yrmean[year]
            wyrtot = wyrmean.get(year, 0)
        res += ("%s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s\n") % (
            year,
            p(grouped, year, 1, varname, prec),
            p(grouped, year, 2, varname, prec),
            p(grouped, year, 3, varname, prec),
            p(grouped, year, 4, varname, prec),
            p(grouped, year, 5, varname, prec),
            p(grouped, year, 6, varname, prec),
            p(grouped, year, 7, varname, prec),
            p(grouped, year, 8, varname, prec),
            p(grouped, year, 9, varname, prec),
            p(grouped, year, 10, varname, prec),
            p(grouped, year, 11, varname, prec),
            p(grouped, year, 12, varname, prec),
            myformat(yrtot, 2),
            myformat(wyrtot, 2),
        )
    yrtot = (
        yrmean.mean() if varname not in ["precip", "snow"] else yrsum.mean()
    )
    wyrtot = (
        wyrmean.mean() if varname not in ["precip", "snow"] else wyrsum.mean()
    )
    res += (
        "MEAN%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f"
        "%6.2f%6.2f%6.2f%6.2f\n"
    ) % (
        df[df["month"] == 1][varname].mean(),
        df[df["month"] == 2][varname].mean(),
        df[df["month"] == 3][varname].mean(),
        df[df["month"] == 4][varname].mean(),
        df[df["month"] == 5][varname].mean(),
        df[df["month"] == 6][varname].mean(),
        df[df["month"] == 7][varname].mean(),
        df[df["month"] == 8][varname].mean(),
        df[df["month"] == 9][varname].mean(),
        df[df["month"] == 10][varname].mean(),
        df[df["month"] == 11][varname].mean(),
        df[df["month"] == 12][varname].mean(),
        yrtot,
        wyrtot,
    )

    # create a better resulting dataframe
    resdf = pd.DataFrame(index=years)
    resdf.index.name = "YEAR"
    for i, month_abbr in enumerate(calendar.month_abbr[1:], start=1):
        col = month_abbr.upper()
        resdf[col] = df[df["month"] == i].set_index("year")[varname]
        resdf.at["MEAN", col] = df[df["month"] == i][varname].mean()
    resdf["ANN"] = yrmean if varname not in ["precip", "snow"] else yrsum
    resdf.at["MEAN", "ANN"] = resdf["ANN"].mean()
    resdf["WATER YEAR"] = (
        wyrmean if varname not in ["precip", "snow"] else wyrsum
    )
    resdf.at["MEAN", "WATER YEAR"] = resdf["WATER YEAR"].mean()
    y1 = int(fdict.get("syear", 1990))

    fig, ax = figure_axes(
        title=f"{ctx['_sname']} {LABELS[varname]}",
        apctx=ctx,
    )
    filtered = df[(df["year"] >= y1) & (df["year"] <= (y1 + 20))]
    if filtered.empty or filtered[varname].isnull().all():
        raise NoDataFound("No data for specified period")
    df2 = filtered[["month", "year", varname]].pivot(
        index="year", columns="month", values=varname
    )
    df2 = pd.concat(
        [df2, df[["month", varname]].groupby("month").mean().transpose()]
    )
    df2.index.values[-1] = "MEAN"
    ax = sns.heatmap(
        df2,
        annot=True,
        fmt=FMT[varname],
        linewidths=0.5,
        ax=ax,
        cmap=ctx["cmap"],
    )
    ax.set_xticklabels(calendar.month_abbr[1:])

    return fig, resdf, res


if __name__ == "__main__":
    plotter({})
