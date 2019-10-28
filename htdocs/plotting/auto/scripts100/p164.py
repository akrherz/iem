"""NWSLI stations over/under"""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

MDICT = OrderedDict(
    [
        ("high", "High Temperature"),
        ("low", "Low Temperature"),
        ("precip", "Reported Precip"),
        ("snow", "Reported Snowfall"),
    ]
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This chart presents a simple accounting of the
    percentage of first order NWS climate sites that are either above or
    below average or reporting precipitation / snow each day.  Note that no
    spatial weighting is done, so one should not interpret this as an areal
    coverage of some condition.  For temperature, sites with an average
    temperature for that date are omitted.
    """
    sts = datetime.date.today() - datetime.timedelta(days=45)
    ets = datetime.date.today() - datetime.timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="date",
            name="sts",
            default=sts.strftime("%Y/%m/%d"),
            label="Select Start Date (inclusive)",
            min="2007/01/09",
        ),
        dict(
            type="date",
            name="ets",
            default=ets.strftime("%Y/%m/%d"),
            label="Select End Date (inclusive)",
            min="2007/01/09",
        ),
        dict(
            type="select",
            name="var",
            default="high",
            options=MDICT,
            label="Which Metric to Plot",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("iem")
    ctx = get_autoplot_context(fdict, get_description())

    sts = ctx["sts"]
    ets = ctx["ets"]
    varname = ctx["var"]

    df = read_sql(
        """
    WITH data as (
        SELECT valid, high - high_normal as high_delta,
        low - low_normal as low_delta, precip, snow
        from cli_data where valid >= %s and valid <= %s
        and substr(station, 1, 1) = 'K'
    )
    SELECT valid,
    sum(case when high_delta > 0 then 1 else 0 end) as high_above,
    sum(case when high_delta = 0 then 1 else 0 end) as high_equal,
    sum(case when high_delta < 0 then 1 else 0 end) as high_below,
    sum(case when low_delta > 0 then 1 else 0 end) as low_above,
    sum(case when low_delta = 0 then 1 else 0 end) as low_equal,
    sum(case when low_delta < 0 then 1 else 0 end) as low_below,
    sum(case when precip > 0 then 1 else 0 end) as precip_above,
    sum(case when precip = 0 then 1 else 0 end) as precip_below,
    sum(case when snow > 0 then 1 else 0 end) as snow_above,
    sum(case when snow = 0 then 1 else 0 end) as snow_below
    from data GROUP by valid ORDER by valid ASC
    """,
        pgconn,
        params=(sts, ets),
        index_col="valid",
    )
    if df.empty:
        raise NoDataFound("Error, no results returned!")
    for v in ["precip", "snow"]:
        if varname == v:
            xlabel = "<-- No %s %%   |     %s   %% -->" % (
                v.capitalize(),
                v.capitalize(),
            )
        df[v + "_count"] = df[v + "_above"] + df[v + "_below"]
        colors = ["r", "b"]
    for v in ["high", "low"]:
        df[v + "_count"] = (
            df[v + "_above"] + df[v + "_below"] + df[v + "_equal"]
        )
        if varname == v:
            xlabel = "<-- Below Average %    |    Above Average % -->"
        colors = ["b", "r"]

    (fig, ax) = plt.subplots(1, 1)
    ax.barh(
        df.index.values,
        0 - (df[varname + "_below"] / df[varname + "_count"] * 100.0),
        fc=colors[0],
        ec=colors[0],
        align="center",
    )
    ax.barh(
        df.index.values,
        df[varname + "_above"] / df[varname + "_count"] * 100.0,
        fc=colors[1],
        ec=colors[1],
        align="center",
    )
    ax.set_xlim(-100, 100)
    ax.grid(True)
    ax.set_title(
        ("Percentage of CONUS NWS First Order CLImate Sites\n" "(%s - %s) %s")
        % (
            sts.strftime("%-d %b %Y"),
            ets.strftime("%-d %b %Y"),
            MDICT.get(varname),
        )
    )
    ax.set_xlabel(xlabel)
    ticks = [-100, -90, -75, -50, -25, -10, 0, 10, 25, 50, 75, 90, 100]
    ax.set_xticks(ticks)
    ax.set_xticklabels([abs(x) for x in ticks])
    plt.setp(ax.get_xticklabels(), rotation=30)
    ax.set_position([0.2, 0.15, 0.75, 0.75])

    return fig, df


if __name__ == "__main__":
    plotter(dict(network="IA_ASOS", station="AMW"))
