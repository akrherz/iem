"""wind rose"""
import datetime

import numpy as np
import pandas as pd
from windrose.windrose import histogram
from windrose import WindroseAxes
from matplotlib.patches import Rectangle
from sqlalchemy import text
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, drct2text
from pyiem.plot import figure
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

PDICT = {
    "ts": "Thunderstorm (TS) Reported",
    "tmpf_above": "Temperature At or Above Threshold (F)",
    "tmpf_below": "Temperature Below Threshold (F)",
    "dwpf_above": "Dew Point At or Above Threshold (F)",
    "dwpf_below": "Dew Point Below Threshold (F)",
    "relh_above": "Relative Humidity At or Above Threshold (%)",
    "relh_below": "Relative Humidity Below Threshold (%)",
}

MDICT = {
    "all": "No Month/Time Limit",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["defaults"] = {"_r": "88"}
    desc[
        "description"
    ] = """This application generates a wind rose for a given
    criterion being meet. A wind rose plot is a convenient way of summarizing
    wind speed and direction."""
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="select",
            name="opt",
            default="ts",
            label="Which metric to plot?",
            options=PDICT,
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="int",
            name="threshold",
            default="80",
            label="Threshold (when appropriate):",
        ),
    ]
    return desc


def highcharts(fdict):
    """Generate the highcharts variant"""
    ctx = get_context(fdict)
    dir_edges, _, table = histogram(
        ctx["df"]["drct"].values,
        ctx["df"]["smph"].values,
        np.array([0, 2, 5, 7, 10, 15, 20]),
        18,
        True,
    )
    arr = [drct2text(mydir) for mydir in dir_edges]
    return (
        """
    var arr = """
        + str(arr)
        + """;
    $("#ap_container").highcharts({
    series: [{name: '2 - 5',
                    data: """
        + str(list(zip(arr, table[1])))
        + """,
                    _colorIndex: 0},
                   {name: '5 - 7',
                    data: """
        + str(list(zip(arr, table[2])))
        + """,
                    _colorIndex: 1},
                   {name: '7 - 10',
                    data: """
        + str(list(zip(arr, table[3])))
        + """,
                    _colorIndex: 2},
                   {name: '10 - 15',
                    data: """
        + str(list(zip(arr, table[4])))
        + """,
                    _colorIndex: 3},
                   {name: '15 - 20',
                    data: """
        + str(list(zip(arr, table[5])))
        + """,
                    _colorIndex: 4},
                   {name: '20 +',
                    data: """
        + str(list(zip(arr, table[6])))
        + """,
                    _colorIndex: 5}],
    chart: {
            polar: true,
            type: 'column'
    },
    title: {
            'text': '"""
        + ctx["title"]
        + """'
    },
    subtitle: {
            'text': '"""
        + ctx["subtitle"]
        + """'
    },
    pane: {
            'size': '85%'
    },
    legend: {
        title: {text: 'Wind Speed [MPH]'},
            verticalAlign: 'bottom',
            layout: 'horizontal'
    },
    xAxis: {
        'tickInterval': 18./8.,
        'labels': {
                   formatter: function(){
                       var v = this.value.toFixed(1);
                       if (v == '0.0') {return 'N';}
                       if (v == '2.3') {return 'NE';}
                       if (v == '4.5') {return 'E';}
                       if (v == '6.8') {return 'SE';}
                       if (v == '9.0') {return 'S';}
                       if (v == '11.3') {return 'SW';}
                       if (v == '13.5') {return 'W';}
                       if (v == '15.8') {return 'NW';}
                       return v;
                   }
        }
    },
    yAxis: {
            'min': 0,
            'endOnTick': false,
            'showLastLabel': true,
            'title': {
                'text': 'Frequency (%)'
            },
            'reversedStacks': false
        },
    tooltip: {
        positioner: function () {
                return { x: 10, y: 10 };
            },
            'valueSuffix': '%',
            shared: true,
            valueDecimals: 1,
            formatter: function () {
            var s = '<b>' + arr[this.x] +
                    ' ('+ this.points[0].total.toFixed(1)+'%)</b>';

            $.each(this.points, function () {
                s += '<br/>' + this.series.name + ': ' +
                    this.y.toFixed(1) + '%';
            });

            return s;
        },
    },
    plotOptions: {
            'series': {
                'stacking': 'normal',
                'shadow': false,
                'groupPadding': 0,
                'pointPlacement': 'on'
            }
    }
    });
    """
    )


def get_context(fdict):
    """Do the agnostic stuff"""
    ctx = get_autoplot_context(fdict, get_description())
    ctx["station"] = ctx["zstation"]

    if ctx["month"] == "all":
        months = range(1, 13)
    elif ctx["month"] == "fall":
        months = [9, 10, 11]
    elif ctx["month"] == "winter":
        months = [12, 1, 2]
    elif ctx["month"] == "spring":
        months = [3, 4, 5]
    elif ctx["month"] == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime(
            "2000-" + ctx["month"] + "-01", "%Y-%b-%d"
        )
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    limiter = "array_to_string(wxcodes, '') ~* 'TS'"
    title = "Thunderstorm (TS) contained in METAR"
    if ctx["opt"] == "tmpf_above":
        limiter = "round(tmpf::numeric,0) >= %s" % (ctx["threshold"],)
        title = r"Air Temp at or above %s$^\circ$F" % (ctx["threshold"],)
    elif ctx["opt"] == "tmpf_below":
        limiter = "round(tmpf::numeric,0) < %s" % (ctx["threshold"],)
        title = r"Air Temp below %s$^\circ$F" % (ctx["threshold"],)
    elif ctx["opt"] == "dwpf_below":
        limiter = "round(dwpf::numeric,0) < %s" % (ctx["threshold"],)
        title = r"Dew Point below %s$^\circ$F" % (ctx["threshold"],)
    elif ctx["opt"] == "dwpf_above":
        limiter = "round(tmpf::numeric,0) >= %s" % (ctx["threshold"],)
        title = r"Dew Point at or above %s$^\circ$F" % (ctx["threshold"],)
    elif ctx["opt"] == "relh_above":
        limiter = f"relh >= {ctx['threshold']}"
        title = f"Relative Humidity at or above {ctx['threshold']}%"
    elif ctx["opt"] == "relh_below":
        limiter = f"relh < {ctx['threshold']}"
        title = f"Relative Humidity below {ctx['threshold']}%"
    with get_sqlalchemy_conn("asos") as conn:
        ctx["df"] = pd.read_sql(
            text(
                f"""
            SELECT valid at time zone 'UTC' as valid,
            drct, sknt * 1.15 as smph from alldata
            where station = :station and {limiter} and sknt > 0
            and drct >= 0 and
            drct <= 360 and extract(month from valid) in :months
            """
            ),
            conn,
            params={"station": ctx["station"], "months": tuple(months)},
            index_col="valid",
        )
    if ctx["df"].empty:
        raise NoDataFound("No Data Found.")
    minvalid = ctx["df"].index.min()
    maxvalid = ctx["df"].index.max()

    ctx["plottitle"] = (
        f"{minvalid.year}-{maxvalid.year} {ctx['station']} Wind Rose, "
        f"month={ctx['month'].upper()}"
    )
    ctx["title"] = "%s-%s %s Wind Rose, month=%s" % (
        minvalid.year,
        maxvalid.year,
        ctx["station"],
        ctx["month"].upper(),
    )
    ctx["subtitle"] = "%s, %s" % (
        ctx["_nt"].sts[ctx["station"]]["name"],
        title.replace(r"$^\circ$", ""),
    )
    return ctx


def plotter(fdict):
    """Go"""
    ctx = get_context(fdict)

    fig = figure(
        title=ctx["plottitle"],
        subtitle=ctx["subtitle"],
        facecolor="w",
        edgecolor="w",
        apctx=ctx,
    )
    ax = WindroseAxes(fig, [0.08, 0.15, 0.86, 0.7], facecolor="w")
    fig.add_axes(ax)
    ax.bar(
        ctx["df"]["drct"].values,
        ctx["df"]["smph"].values,
        normed=True,
        bins=[0, 2, 5, 7, 10, 15, 20],
        opening=0.8,
        edgecolor="white",
        nsector=18,
    )
    handles = []
    for p in ax.patches_list:
        color = p.get_facecolor()
        handles.append(
            Rectangle((0, 0), 0.1, 0.3, facecolor=color, edgecolor="black")
        )
    legend = fig.legend(
        handles,
        ("2-5", "5-7", "7-10", "10-15", "15-20", "20+"),
        loc=(0.01, 0.03),
        ncol=6,
        title="Wind Speed [mph]",
        mode=None,
        columnspacing=0.9,
        handletextpad=0.45,
    )
    plt.setp(legend.get_texts(), fontsize=10)

    fig.text(
        0.95,
        0.12,
        f"n={len(ctx['df'].index)}",
        verticalalignment="bottom",
        ha="right",
    )

    return fig, ctx["df"]


if __name__ == "__main__":
    plotter(dict(station="AMW", month="jan", opt="tmpf_above", threshold=32))
