"""
This application generates a wind rose for a given
criterion being meet. A wind rose plot is a convenient way of summarizing
wind speed and direction.
"""
import datetime

import numpy as np
import pandas as pd
from metpy.units import units
from pyiem.exceptions import NoDataFound
from pyiem.plot.windrose import WindrosePlot, histogram
from pyiem.util import drct2text, get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

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
RAMPS = {
    "20": "2, 5, 7, 10, 15, 20 MPH",
    "40": "2, 5, 10, 20, 30, 40 MPH",
    "60": "2, 10, 20, 30, 40, 60 MPH",
    "80": "2, 10, 20, 40, 60, 80 MPH",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "defaults": {"_r": "88"}}
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
        dict(
            type="select",
            name="r",
            label="Select wind speed binning interval to use for plot",
            default="20",
            options=RAMPS,
        ),
    ]
    return desc


def get_ramp(ctx):
    """np.array for the ramp."""
    label = RAMPS[ctx["r"]].replace(" MPH", "")
    arr = [int(v) for v in label.split(",")]
    arr.insert(0, 0)
    return np.array(arr)


def highcharts(fdict):
    """Generate the highcharts variant"""
    ctx = get_context(fdict)
    bins = get_ramp(ctx)
    _, dir_edges, table = histogram(
        units("mile / hour") * ctx["df"]["smph"].values,
        units("degree") * ctx["df"]["drct"].values,
        units("mile / hour") * bins[1:],
        16,
    )
    table = table.m
    dir_edges = dir_edges.m
    arr = [drct2text(mydir) for mydir in dir_edges]
    containername = fdict.get("_e", "ap_container")
    return f"""
    var arr = {arr};
    Highcharts.chart("{containername}", {{
        series: [
        {{
            name: '{bins[1]} - {bins[2]}',
            data: {str(list(table[:, 0]))},
            pointInterval: 22.5,
            _colorIndex: 0
        }},
        {{name: '{bins[2]} - {bins[3]}',
        data: {str(list(table[:, 1]))},
            pointInterval: 22.5,
        _colorIndex: 1}},
        {{name: '{bins[3]} - {bins[4]}',
        data: {str(list(table[:, 2]))},
            pointInterval: 22.5,
        _colorIndex: 2}},
        {{name: '{bins[4]} - {bins[5]}',
        data: {str(list(table[:, 3]))},
            pointInterval: 22.5,
        _colorIndex: 3}},
        {{name: '{bins[5]} - {bins[6]}',
        data: {str(list(table[:, 4]))},
            pointInterval: 22.5,
        _colorIndex: 4}},
        {{name: '{bins[6]} +',
        data: {str(list(table[:, 5]))},
            pointInterval: 22.5,
        _colorIndex: 5}}
        ],
    chart: {{
            polar: true,
            type: 'column'
    }},
    title: {{
            'text': '{ctx["title"]}'
    }},
    subtitle: {{
        'text': '{ctx["subtitle"]}'
    }},
    pane: {{
        startAngle: 0,
        endAngle: 360,
        'size': '85%'
    }},
    legend: {{
        title: {{text: 'Wind Speed [MPH]'}},
            verticalAlign: 'bottom',
            layout: 'horizontal'
    }},
    xAxis: {{
        tickInterval: 22.5,
        min: 0,
        max: 360
    }},
    yAxis: {{
            'min': 0,
            'endOnTick': false,
            'showLastLabel': true,
            'title': {{
                'text': 'Frequency (%)'
            }},
            'reversedStacks': false
        }},
    tooltip: {{
        positioner: function () {{
                return {{ x: 10, y: 10 }};
            }},
            'valueSuffix': '%',
            shared: true,
            valueDecimals: 1,
            formatter: function () {{
            var s = '<b>' + arr[this.x] +
                    ' ('+ this.points[0].total.toFixed(1)+'%)</b>';

            $.each(this.points, function () {{
                s += '<br/>' + this.series.name + ': ' +
                    this.y.toFixed(1) + '%';
            }});

            return s;
        }},
    }},
        plotOptions: {{
            'series': {{
                'stacking': 'normal',
                'shadow': false,
                'groupPadding': 0,
                'pointPlacement': 'on'
            }}
        }}
    }});
    """


def get_context(fdict):
    """Do the agnostic stuff"""
    ctx = get_autoplot_context(fdict, get_description())
    ctx["station"] = ctx["zstation"]

    if ctx["month"] == "all":
        months = list(range(1, 13))
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
    params = {
        "thres": ctx["threshold"],
        "station": ctx["station"],
        "months": months,
    }
    if ctx["opt"] == "tmpf_above":
        limiter = "round(tmpf::numeric,0) >= :thres"
        title = f"Air Temp at or above {ctx['threshold']}" r"$^\circ$F"
    elif ctx["opt"] == "tmpf_below":
        limiter = "round(tmpf::numeric,0) < :thres"
        title = f"Air Temp below {ctx['threshold']}" r"$^\circ$F"
    elif ctx["opt"] == "dwpf_below":
        limiter = "round(dwpf::numeric,0) < :thres"
        title = f"Dew Point below {ctx['threshold']}" r"$^\circ$F"
    elif ctx["opt"] == "dwpf_above":
        limiter = "round(tmpf::numeric,0) >= :thres"
        title = f"Dew Point at or above {ctx['threshold']}" r"$^\circ$F"
    elif ctx["opt"] == "relh_above":
        limiter = "relh >= :thres"
        title = f"Relative Humidity at or above {ctx['threshold']}%"
    elif ctx["opt"] == "relh_below":
        limiter = "relh < :thres"
        title = f"Relative Humidity below {ctx['threshold']}%"
    with get_sqlalchemy_conn("asos") as conn:
        ctx["df"] = pd.read_sql(
            text(
                f"""
            SELECT valid at time zone 'UTC' as valid,
            drct, sknt * 1.15 as smph from alldata
            where station = :station and {limiter} and sknt > 0
            and drct >= 0 and
            drct <= 360 and extract(month from valid) = ANY(:months)
            """
            ),
            conn,
            params=params,
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
    ctx["title"] = (
        f"{minvalid.year}-{maxvalid.year} {ctx['station']} Wind Rose, "
        f"month={ctx['month'].upper()}"
    )
    ctx["subtitle"] = "%s, %s" % (
        ctx["_nt"].sts[ctx["station"]]["name"],
        title.replace(r"$^\circ$", ""),
    )
    return ctx


def plotter(fdict):
    """Go"""
    ctx = get_context(fdict)

    wr = WindrosePlot(
        title=ctx["plottitle"],
        subtitle=ctx["subtitle"],
        rect=[0.08, 0.15, 0.86, 0.7],
    )
    bins = units("mile / hour") * get_ramp(ctx)[1:]
    wr.barplot(
        units("degree") * ctx["df"]["drct"].values,
        units("mile / hour") * ctx["df"]["smph"].values,
        normed=True,
        bins=bins,
        opening=0.8,
        edgecolor="white",
        nsector=16,
    )

    return wr.fig, ctx["df"]


if __name__ == "__main__":
    highcharts(
        {
            "station": "AMW",
            "month": "all",
            "opt": "ts",
            "threshold": 32,
        }
    )
