"""
This chart plots the monthly percentiles that
a given daily value has.  For example, where would a daily 2 inch
precipitation rank for each month of the year.  Having a two inch event
in December would certainly rank higher than one in May. Percentiles
for precipitation are computed with dry days omitted.
"""

import calendar
import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

from iemweb.autoplot import ARG_STATION

PDICT = {
    "high": "High Temperature",
    "low": "Low Temperature",
    "precip": "Precipitation",
}

PDICT2 = {"above": "At or Above", "below": "Below"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
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
        ARG_STATION,
    ]
    return desc


def get_context(fdict):
    """Get the context"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"].upper()
    varname = ctx["var"]
    level = ctx["level"]
    mydir = ctx["dir"]
    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("Unknown station metadata.")

    plimit = "" if varname != "precip" else " and precip > 0.009 "
    comp = ">=" if mydir == "above" else "<"
    if varname in ["high", "low"]:
        level = int(level)
    with get_sqlalchemy_conn("coop") as conn:
        monthly = pd.read_sql(
            f"""
        SELECT month, year,
        sum(case when {varname} {comp} %s then 1 else 0 end) as hits,
        count(*) from alldata WHERE station = %s {plimit}
        and day < %s
        GROUP by year, month ORDER by year desc, month ASC
        """,
            conn,
            params=(level, station, datetime.date.today().replace(day=1)),
            index_col=None,
        )
    if monthly.empty:
        raise NoDataFound("Did not find any data.")
    quorum = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    monthly["quorum"] = monthly["month"].apply(lambda x: quorum[x])
    if varname != "precip":
        monthly = monthly[monthly["count"] >= monthly["quorum"]]
    years = monthly["month"].value_counts()
    df = monthly.groupby("month").agg({"hits": "sum", "count": "sum"}).copy()
    df["hits_max"] = monthly.groupby("month").agg({"hits": "max"})["hits"]
    df["hits_max_year"] = monthly.loc[
        monthly.groupby("month").agg({"hits": "idxmax"})["hits"]
    ].set_index("month")["year"]
    df["hits_min"] = monthly.groupby("month").agg({"hits": "min"})["hits"]
    df["hits_min_year"] = monthly.loc[
        monthly.groupby("month").agg({"hits": "idxmin"})["hits"]
    ].set_index("month")["year"]
    df["rank"] = (df["count"] - df["hits"]) / df["count"] * 100.0
    df["avg_days"] = df["hits"] / years
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
    """Go"""
    ctx = get_context(fdict)
    containername = fdict.get("_e", "ap_container")

    return f"""
Highcharts.chart('{containername}', {{
    title: {{text: '{ctx['title']}'}},
    subtitle: {{text: '{ctx['subtitle']}'}},
    yAxis: [{{
            min: 0, max: 100,
            title: {{
                text: 'Percentile'
            }}
        }}, {{
            min: 0,
            title: {{
                text: 'Avg Days per Month'
            }},
            opposite: true
    }}],
    tooltip: {{
            shared: true,
            formatter: function() {{
                var s = '<b>' + this.x +'</b>';
                s += '<br /><b>Percentile:</b> '+ this.points[0].y.toFixed(2);
s += '<br /><b>Avg Days per Month:</b> '+ this.points[1].y.toFixed(2);
                return s;
            }}
    }},
    plotOptions: {{
            column: {{
                grouping: false,
                shadow: false,
                borderWidth: 0
            }}
    }},
    series : [{{
        name: 'Percentile',
        data: {ctx['df']['rank'].values.tolist()},
        pointPadding: 0.2,
        pointPlacement: -0.2
    }},{{
        name: 'Avg Days per Month',
        data: {ctx['df']['avg_days'].values.tolist()},
        yAxis: 1,
        pointPadding: 0.4,
        pointPlacement: -0.2
    }}],
    chart: {{type: 'column'}},
    xAxis: {{categories: {calendar.month_abbr[1:]}}}
}});
    """


def plotter(fdict):
    """Go"""
    ctx = get_context(fdict)
    (fig, ax) = figure_axes(
        title=ctx["title"], subtitle=ctx["subtitle"], apctx=ctx
    )
    ax.set_position([0.1, 0.2, 0.8, 0.7])
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

    ax.grid(True)
    ax.set_ylabel("Percentile [%]", color="tan")
    ax.set_ylim(0, 105)
    ax2 = ax.twinx()
    ax2.bar(
        df.index.values,
        df["avg_days"],
        width=-0.4,
        align="edge",
        fc="blue",
        ec="k",
        zorder=1,
    )
    ax2.set_ylabel(
        f"Avg Days per Month ({df['avg_days'].sum():.2f} days per year)",
        color="b",
    )
    ax2.set_ylim(0, 32)
    ax.set_xticks(range(1, 13))
    labels = []
    for i in range(1, 13):
        labels.append(  # noqa
            f"{calendar.month_abbr[i]}\n"
            f"{df.at[i, 'hits_min']:.0f}:{df.at[i, 'hits_min_year']:.0f}\n"
            f"{df.at[i, 'hits_max']:.0f}:{df.at[i, 'hits_max_year']:.0f}"
        )
    ax.set_xticklabels(labels)
    ax.set_xlabel("Month of the Year (min+min days for month and last year)")
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
        ax2.text(
            idx,
            row["avg_days"],
            f"{row['avg_days']:.1f}",
            ha="right",
            color="k",
            zorder=5,
            fontsize=11,
        )

    return fig, df
