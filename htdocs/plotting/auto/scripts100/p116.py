"""
This chart presents monthly cooling degree days
or heating degree days for a 20 year period of your choice.  The 20 year
limit is for plot usability only, the data download has all available
years contained.
"""
import datetime

import pandas as pd
import seaborn as sns
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {"cdd": "Cooling Degree Days", "hdd": "Heating Degree Days"}


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
            options=PDICT,
            default="cdd",
            name="var",
            label="Select Variable",
        ),
        dict(
            type="year",
            name="syear",
            default=y20,
            label="For plotting, year to start 20 years of plot",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["station"]
    varname = ctx["var"]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            SELECT year, month, sum(precip) as sum_precip,
            avg(high) as avg_high,
            avg(low) as avg_low,
            sum(cdd(high,low,60)) as cdd60,
            sum(cdd(high,low,65)) as cdd65,
            sum(hdd(high,low,60)) as hdd60,
            sum(hdd(high,low,65)) as hdd65,
            sum(case when precip > 0.009 then 1 else 0 end) as rain_days,
            sum(case when snow >= 0.1 then 1 else 0 end) as snow_days
            from alldata WHERE station = %s GROUP by year, month
        """,
            conn,
            params=(station,),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["monthdate"] = df[["year", "month"]].apply(
        lambda x: datetime.date(x.iloc[0], x.iloc[1], 1), axis=1
    )
    df = df.set_index("monthdate")

    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        f"# Report Generated: {datetime.date.today():%d %b %Y}\n"
        f"# Climate Record: {ctx['_nt'].sts[station]['archive_begin']} "
        f"-> {datetime.date.today()}\n"
        f"# Site Information: {ctx['_sname']}\n"
        "# Contact Information: Daryl Herzmann "
        "akrherz@iastate.edu 515.294.5978\n"
        f"# THESE ARE THE MONTHLY {PDICT[varname].upper()} (base=65) "
        f"FOR STATION {station}\n"
        "YEAR    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    "
        "SEP    OCT    NOV    DEC\n"
    )

    second = (
        f"# THESE ARE THE MONTHLY {PDICT[varname].upper()} (base=60) "
        f"FOR STATION {station}\n"
        "YEAR    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    "
        "SEP    OCT    NOV    DEC\n"
    )
    minyear = df["year"].min()
    maxyear = df["year"].max()
    for yr in range(minyear, maxyear + 1):
        res += f"{yr:4.0f}"
        second += f"{yr:4.0f}"
        for mo in range(1, 13):
            ts = datetime.date(yr, mo, 1)
            if ts not in df.index:
                res += f"{'M':>7s}"
                second += f"{'M':>7s}"
                continue
            row = df.loc[ts]
            val = row[f"{varname}65"]
            res += f"{val:7.0f}"
            val = row[f"{varname}60"]
            second += f"{val:7.0f}"
        res += "\n"
        second += "\n"

    res += "MEAN"
    second += "MEAN"
    for mo in range(1, 13):
        df2 = df[df["month"] == mo]
        val = df2[f"{varname}65"].mean()
        res += f"{val:7.0f}"
        val = df2[varname + "60"].mean()
        second += f"{val:7.0f}"
    res += "\n"
    second += "\n"
    res += second

    y1 = int(fdict.get("syear", 1990))

    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']} " f"({y1}-{y1 + 20})"
    )
    fig, ax = figure_axes(
        title=title,
        subtitle=f"{PDICT[varname]} base=60" r"$^\circ$F",
        apctx=ctx,
    )
    filtered = df[(df["year"] >= y1) & (df["year"] <= (y1 + 20))]
    if filtered.empty:
        raise NoDataFound("No data for specified period")
    df2 = filtered[["month", "year", varname + "60"]].pivot(
        index="year", columns="month", values=f"{varname}60"
    )
    sns.heatmap(df2, annot=True, fmt=".0f", linewidths=0.5, ax=ax)

    return fig, df, res


if __name__ == "__main__":
    plotter({})
