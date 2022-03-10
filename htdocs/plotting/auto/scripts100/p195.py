"""Storm Motion 2D Histogram."""
# pylint: disable=consider-using-f-string
import datetime
import json

import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, convert_value
from pyiem.exceptions import NoDataFound
import seaborn as sns
from sqlalchemy import text


PDICT = {
    "TO": "Tornado Warning",
    "SV": "Severe Thunderstorm Warning",
    "_A": "Severe Tstorm + Tornado Warning",
    "EW": "Extreme Wind",
    "FA": "Flood Advisory/Warning",
    "FF": "Flash Flood Warning",
    "MA": "Marine Warning",
    "SQ": "Snow Squall",
}
PDICT2 = {
    "NEW": "at Issuance",
    "ANY": "at Issuance or Update",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 600
    desc[
        "description"
    ] = """Some of the warnings that the National Weather
    Service issues includes a storm motion vector.  This application
    plots the speed vs direction of the vector and includes a kernel density
    estimate (KDE) overlay.  You can optionally pick a date to highlight on the
    chart.  This date is a central time zone date.
    """
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="date",
            name="date",
            default=today.strftime("%Y/%m/%d"),
            label="Optional Date to Highlight on Map:",
            min="2007/07/16",
            max=today.strftime("%Y/%m/%d"),
            optional=True,
        ),
        dict(
            type="networkselect",
            name="wfo",
            default="DMX",
            label="Select Forecast Office:",
            network="WFO",
        ),
        dict(
            type="select",
            name="p",
            default="TO",
            options=PDICT,
            label="Warning Type:",
        ),
        dict(
            type="select",
            name="limit",
            default="NEW",
            options=PDICT2,
            label="Include only issuance or also updated (SVS, etc):",
        ),
    ]
    return desc


def get_data(ctx):
    """Do the data fetching portion of this autoplot's work."""
    statuslimit = "status = 'NEW'"
    phenomena = ctx["p"]
    wfo = ctx["wfo"]
    title = "at Issuance"
    if ctx["limit"] == "ANY":
        title = "at Issuance or Update"
        statuslimit = "status != 'CAN'"
    ps = [phenomena]
    if phenomena == "_A":
        ps = ["TO", "SV"]
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                "SELECT polygon_begin at time zone 'America/Chicago' "
                "as issue, to_char(polygon_begin at time zone 'UTC', "
                "'YYYY-MM-DD HH24:MI') as utc_issue, eventid, "
                "phenomena as ph, significance as s, tml_direction, tml_sknt "
                "from sbw WHERE phenomena in :phenomena and wfo = :wfo and "
                f"{statuslimit} and tml_direction is not null and "
                "tml_sknt is not null ORDER by issue"
            ),
            conn,
            params={"phenomena": tuple(ps), "wfo": wfo},
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["tml_mph"] = convert_value(df["tml_sknt"], "knot", "mile / hour")
    ctx["title"] = (
        f"NWS {ctx['_nt'].sts[wfo]['name']}\n"
        f"{PDICT[phenomena]} Storm Motion {title}\n"
        f"{len(df.index)} events ploted between "
        f"{df['issue'].min().date():%b %-d, %Y} and "
        f"{df['issue'].max().date():%b %-d, %Y}"
    )
    return df


def highcharts(fdict):
    """Do the highcharts scatter plot of the data."""
    ctx = get_autoplot_context(fdict, get_description())
    df = get_data(ctx)
    df["datetxt"] = df["issue"].dt.strftime("%b %-d, %Y")
    date = ctx.get("date")
    plotdf = df
    if date:
        plotdf = df[df["issue"].dt.date != date]
    cols = (
        "tml_direction tml_mph datetxt tml_sknt utc_issue ph s eventid"
    ).split()
    series = [
        dict(
            name="All Events",
            data=(
                plotdf[cols]
                .rename(columns={"tml_direction": "x", "tml_mph": "y"})
                .to_dict(orient="records")
            ),
        )
    ]
    if date:
        series.append(
            dict(
                name=date.strftime("%b %-d, %Y"),
                data=(
                    df[df["issue"].dt.date == date][cols]
                    .rename(columns={"tml_direction": "x", "tml_mph": "y"})
                    .to_dict(orient="records")
                ),
            )
        )
    return """
    $("#ap_container").highcharts({
        chart: {
            type: 'scatter',
            zoomType: 'xy'
        },
        title: {
            text: '%s'
        },
        xAxis: {
            title: {
                enabled: true,
                text: 'Direction (degrees)'
            },
            startOnTick: true,
            endOnTick: true,
            showLastLabel: true
        },
        yAxis: {
            title: {
                text: 'Speed (MPH)'
            }
        },
        tooltip: {
            valueDecimals: 1,
            formatter: function() {
                return '<b>'+ this.point.datetxt +'</b><br /> '+
                    this.point.tml_sknt +' KT ('+
                    this.point.y.toFixed(1) +' MPH)<br />'+
                    'From: '+ this.point.x +'°<br />'+
                    'UTC: '+ this.point.utc_issue +'Z<br />'+
                    'VTEC: '+ this.point.ph +'.'+ this.point.s +
                    ' #'+ this.point.eventid
                ;
            }
        },
        series: %s
    });
    """ % (
        ctx["title"].replace("\n", "<br>"),
        json.dumps(series),
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    date = ctx.get("date")
    df = get_data(ctx)
    plotdf = df
    if date is not None:
        plotdf = df[df["issue"].dt.date != date]

    g = sns.jointplot(
        x=plotdf["tml_direction"].values,
        y=plotdf["tml_mph"],
        s=40,
        zorder=1,
        color="tan",
        xlim=(0, 360),
    ).plot_joint(sns.kdeplot, n_levels=6)
    figure(fig=g.figure, apctx=ctx, title=ctx["title"])
    g.ax_joint.set_xlabel("Storm Motion From Direction")
    g.ax_joint.set_ylabel("Storm Speed [MPH]")
    g.ax_joint.set_xticks(range(0, 361, 45))
    g.ax_joint.set_xticklabels("N NE E SE S SW W NW N".split())
    if date:
        df2 = df[df["issue"].dt.date == date]
        g.ax_joint.scatter(
            df2["tml_direction"],
            df2["tml_mph"],
            marker="+",
            color="r",
            s=50,
            label=date.strftime("%b %-d, %Y"),
            zorder=2,
        )
        g.ax_joint.legend(loc="best")
    g.ax_joint.grid()
    g.fig.subplots_adjust(top=0.9, bottom=0.1, left=0.1)
    return g.fig, df


if __name__ == "__main__":
    highcharts({})
