"""Monthly percentiles"""
import calendar
import datetime
from collections import OrderedDict

import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    [
        ("high", "High Temperature"),
        ("low", "Low Temperature"),
        ("precip", "Precipitation"),
    ]
)

PDICT2 = {"above": "At or Above", "below": "Below"}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This chart plots the monthly percentiles that
    a given daily value has.  For example, where would a daily 2 inch
    precipitation rank for each month of the year.  Having a two inch event
    in December would certainly rank higher than one in May. Percentiles
    for precipitation are computed with dry days omitted."""
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT,
            name="var",
            label="Select Variable to Plot",
            default="precip",
        ),
        dict(
            type="select",
            options=PDICT2,
            name="dir",
            label="Direction of Percentile",
            default="above",
        ),
        dict(
            type="float",
            name="level",
            default="2",
            label="Daily Variable Level (inch or degrees F):",
        ),
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
    ]
    return desc


def get_context(fdict):
    """ Get the context """
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"].upper()
    varname = ctx["var"]
    level = ctx["level"]
    mydir = ctx["dir"]
    table = "alldata_%s" % (station[:2],)
    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("Unknown station metadata.")
    years = datetime.date.today().year - bs.year + 1.0

    plimit = "" if varname != "precip" else " and precip > 0.009 "
    comp = ">=" if mydir == "above" else "<"
    df = read_sql(
        f"""
    SELECT month,
    sum(case when {varname} {comp} %s then 1 else 0 end) as hits,
    count(*) from {table} WHERE station = %s {plimit}
    GROUP by month ORDER by month ASC
    """,
        pgconn,
        params=(level, station),
        index_col="month",
    )
    df["rank"] = (df["count"] - df["hits"]) / df["count"] * 100.0
    df["avg_days"] = df["hits"] / years
    df["return_interval"] = 1.0 / df["avg_days"]
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    ctx["df"] = df
    ctx["station"] = station
    ctx["mydir"] = mydir
    ctx["level"] = level
    ctx["varname"] = varname
    units = "inch" if varname in ["precip"] else "F"
    ctx["title"] = ("Monthly Frequency of Daily %s %s %s+ %s") % (
        PDICT[varname],
        PDICT2[mydir],
        level,
        units,
    )
    ctx["subtitle"] = ("for [%s] %s (%s-%s)") % (
        station,
        ctx["_nt"].sts[station]["name"],
        bs.year,
        datetime.date.today().year,
    )
    return ctx


def highcharts(fdict):
    """ Go """
    ctx = get_context(fdict)

    return (
        """
    var avg_days = """
        + str(ctx["df"]["avg_days"].values.tolist())
        + """;
$("#ap_container").highcharts({
    title: {text: '"""
        + ctx["title"]
        + """'},
    subtitle: {text: '"""
        + ctx["subtitle"]
        + """'},
    yAxis: [{
            min: 0, max: 100,
            title: {
                text: 'Percentile'
            }
        }, {
            min: 0,
            title: {
                text: 'Return Period (years)'
            },
            opposite: true
    }],
    tooltip: {
            shared: true,
            formatter: function() {
                var s = '<b>' + this.x +'</b>';
                s += '<br /><b>Percentile:</b> '+ this.points[0].y.toFixed(2);
s += '<br /><b>Return Interval:</b> '+ this.points[1].y.toFixed(2) +" years";
s += '<br /><b>Avg Days per Month:</b> '+ (1. / this.points[1].y).toFixed(2);
                return s;
            }
    },
    plotOptions: {
            column: {
                grouping: false,
                shadow: false,
                borderWidth: 0
            }
    },
    series : [{
        name: 'Percentile',
        data: """
        + str(ctx["df"]["rank"].values.tolist())
        + """,
        pointPadding: 0.2,
        pointPlacement: -0.2
    },{
        name: 'Return Interval',
        data: """
        + ctx["df"]["return_interval"].to_json(orient="records")
        + """,
        pointPadding: 0.2,
        pointPlacement: 0.2,
        yAxis: 1
    }],
    chart: {type: 'column'},
    xAxis: {categories: """
        + str(calendar.month_abbr[1:])
        + """}

});
    """
    )


def plotter(fdict):
    """ Go """
    ctx = get_context(fdict)
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    df = ctx["df"]

    ax.bar(
        df.index.values,
        df["rank"],
        fc="tan",
        zorder=1,
        ec="orange",
        align="edge",
        width=0.4,
    )

    ax.set_title("%s\n%s" % (ctx["title"], ctx["subtitle"]))
    ax.grid(True)
    ax.set_ylabel("Percentile [%]", color="tan")
    ax.set_ylim(0, 105)
    ax2 = ax.twinx()
    ax2.bar(
        df.index.values,
        df["return_interval"],
        width=-0.4,
        align="edge",
        fc="blue",
        ec="k",
        zorder=1,
    )
    ax2.set_ylabel(
        "Return Interval (years) (%.2f Days per Year)"
        % (df["avg_days"].sum(),),
        color="b",
    )
    ax2.set_ylim(0, df["return_interval"].max() * 1.1)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0.5, 12.5)
    for idx, row in df.iterrows():
        ax.text(
            idx,
            row["rank"],
            "%.1f" % (row["rank"],),
            ha="left",
            color="k",
            zorder=5,
            fontsize=11,
        )
        if not np.isnan(row["return_interval"]):
            ax2.text(
                idx,
                row["return_interval"],
                "%.1f" % (row["return_interval"],),
                ha="right",
                color="k",
                zorder=5,
                fontsize=11,
            )
        else:
            ax2.text(idx, 0.0, "n/a", ha="right")

    return fig, df


if __name__ == "__main__":
    plotter(dict())
