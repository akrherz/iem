"""Stddev of temperatures"""
import calendar

from pandas.io.sql import read_sql
from pyiem import network
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {"high": "High Temperature", "low": "Low Temperature"}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This chart presents two measures of temperature
    variability.  The first is the standard deviation of the period of
    record for a given day of the year.  The second is the standard deviation
    of the day to day changes in temperature.
    """
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
            default="high",
            label="Which Daily Variable:",
            options=PDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["var"]
    if PDICT.get(varname) is None:
        return

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    df = read_sql(
        """
    with data as (
        select extract(doy from day) as doy,
        day, """
        + varname
        + """ as v from """
        + table
        + """ WHERE
        station = %s),
    doyagg as (
        SELECT doy, stddev(v) from data GROUP by doy),
    deltas as (
        SELECT doy, (v - lag(v) OVER (ORDER by day ASC)) as d from data),
    deltaagg as (
        SELECT doy, stddev(d) from deltas GROUP by doy)

    SELECT d.doy, d.stddev as d2d_stddev,
    y.stddev as doy_stddev from deltaagg d JOIN doyagg y ON
    (y.doy = d.doy) WHERE d.doy < 366 ORDER by d.doy ASC
    """,
        pgconn,
        params=(station,),
        index_col="doy",
    )

    fig, ax = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
    ax[0].plot(
        df.index.values, df["doy_stddev"], lw=2, color="r", label="Single Day"
    )
    ax[0].plot(
        df.index.values, df["d2d_stddev"], lw=2, color="b", label="Day to Day"
    )
    ax[0].legend(loc="best", fontsize=10, ncol=2)

    ax[0].set_ylabel(r"Temperature Std. Deviation $^\circ$F")
    ax[0].grid(True)

    msg = ("[%s] %s Daily %s Standard Deviations") % (
        station,
        nt.sts[station]["name"],
        PDICT.get(varname),
    )
    tokens = msg.split()
    sz = int(len(tokens) / 2)
    ax[0].set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))

    ax[1].plot(
        df.index.values, df["doy_stddev"] / df["d2d_stddev"], lw=2, color="g"
    )
    ax[1].set_ylabel("Ratio SingleDay/Day2Day")
    ax[1].grid(True)
    ax[1].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].set_xlim(0, 366)
    return fig, df


if __name__ == "__main__":
    plotter(dict())
