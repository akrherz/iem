"""talltowers plot"""
import datetime

import pytz
import numpy as np
from pandas.io.sql import read_sql
import matplotlib.dates as mdates
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents one second data from the
    Iowa Atmospheric Observatory Tall-Towers sites overseen by Dr Gene Takle.
    The plot limits the number of times plotted to approximately 1,000 so to
    prevent web browser crashes.  If you select a time period greater than
    20 minutes, you will get strided results."""
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            default="ETTI4",
            label="Select Station",
            network="TALLTOWERS",
        ),
        dict(
            type="datetime",
            name="dt",
            default="2016/09/15 2340",
            label="Start Time (UTC Time Zone):",
            min="2016/04/01 0000",
        ),
        dict(
            type="int",
            name="minutes",
            default=10,
            label="Number of Minutes to Plot",
        ),
    ]
    return desc


def get_context(fdict):
    """Get plot context"""
    pgconn = get_dbconn("talltowers")
    ctx = get_autoplot_context(fdict, get_description())
    ctx["dt"] = ctx["dt"].replace(tzinfo=pytz.UTC)
    dt = ctx["dt"]
    station = ctx["station"]
    minutes = ctx["minutes"]
    # We can't deal with thousands of datapoints on the plot, so we stride
    # appropriately with hopes of limiting to 1000 x points
    size = minutes * 60.0
    stride = 1 if size < 1000 else int(((size / 1000) + 1))

    towerid = ctx["_nt"].sts[station]["remote_id"]
    ctx["title"] = "Tall Tower %s" % (ctx["_nt"].sts[station]["name"],)

    ctx["df"] = read_sql(
        """
        WITH data as (
            SELECT *, row_number() OVER (ORDER by valid ASC)
            from data_analog where tower = %s and
            valid between %s and %s ORDER by valid ASC)
        select * from data where row_number %% %s = 0
    """,
        pgconn,
        params=(towerid, dt, dt + datetime.timedelta(minutes=minutes), stride),
        index_col="valid",
    )
    return ctx


def highcharts(fdict):
    """Do highcharts variant"""
    ctx = get_context(fdict)
    df = ctx["df"]
    df["ticks"] = df.index.values.astype(np.int64) // 10 ** 6
    lines = []
    lines2 = []
    lines3 = []
    lines4 = []
    for col in [
        "ws_5m_s",
        "ws_5m_nw",
        "ws_10m_s",
        "ws_10m_nwht",
        "ws_20m_s",
        "ws_20m_nw",
        "ws_40m_s",
        "ws_40m_nwht",
        "ws_80m_s",
        "ws_80m_nw",
        "ws_120m_s",
        "ws_120m_nwht",
    ]:
        vals = df[["ticks", col]].to_json(orient="values")
        lines.append(
            """{
            name: '"""
            + col
            + """',
            type: 'line',
            tooltip: {valueDecimal: 1},
            data: """
            + vals
            + """
            }
        """
        )
    for col in [
        "airtc_5m",
        "airtc_10m",
        "airtc_20m",
        "airtc_40m",
        "airtc_80m",
        "airtc_120m_1",
        "airtc_120m_2",
    ]:
        vals = df[["ticks", col]].to_json(orient="values")
        lines2.append(
            """{
            name: '"""
            + col
            + """',
            type: 'line',
            tooltip: {valueDecimal: 1},
            data: """
            + vals
            + """
            }
        """
        )
    for col in [
        "rh_5m",
        "rh_10m",
        "rh_20m",
        "rh_40m",
        "rh_80m",
        "rh_120m_1",
        "rh_120m_2",
    ]:
        vals = df[["ticks", col]].to_json(orient="values")
        lines3.append(
            """{
            name: '"""
            + col
            + """',
            type: 'line',
            tooltip: {valueDecimal: 1},
            data: """
            + vals
            + """
            }
        """
        )
    for col in [
        "winddir_5m_s",
        "winddir_5m_nw",
        "winddir_10m_s",
        "winddir_10m_nw",
        "winddir_20m_s",
        "winddir_20m_nw",
        "winddir_40m_s",
        "winddir_40m_nw",
        "winddir_80m_s",
        "winddir_80m_nw",
        "winddir_120m_s",
        "winddir_120m_nw",
    ]:
        vals = df[["ticks", col]].to_json(orient="values")
        lines4.append(
            """{
            name: '"""
            + col
            + """',
            type: 'line',
            tooltip: {valueDecimal: 1},
            data: """
            + vals
            + """
            }
        """
        )

    series = ",".join(lines)
    series2 = ",".join(lines2)
    series3 = ",".join(lines3)
    series4 = ",".join(lines4)

    return (
        """
/**
 * In order to synchronize tooltips and crosshairs, override the
 * built-in events with handlers defined on the parent element.
 */
var charts = [],
    options;

/**
 * Synchronize zooming through the setExtremes event handler.
 */
function syncExtremes(e) {
    var thisChart = this.chart;

    if (e.trigger !== 'syncExtremes') { // Prevent feedback loop
        Highcharts.each(Highcharts.charts, function (chart) {
            if (chart !== thisChart) {
                if (chart.xAxis[0].setExtremes) { // It is null while updating
                    chart.xAxis[0].setExtremes(e.min, e.max, undefined, false,
                    { trigger: 'syncExtremes' });
                }
            }
        });
    }
}
function syncTooltip(container, p) {
    Highcharts.each(Highcharts.charts, function (chart) {
        if (container.id != chart.container.id) {
            var d = [];
            for (j=0; j < chart.series.length; j++){
                d[j] = chart.series[j].data[p];
            }
            chart.tooltip.refresh(d[0]);
        }
    });
}
options = {
    time: {useUTC: false},
    chart: {zoomType: 'x'},
    legend: {enabled: true},
    plotOptions: {
        series: {
            cursor: 'pointer',
            allowPointSelect: true,
            point: {
                events: {
                    mouseOver: function () {
                        // Note, I converted this.x to this.index
                        //syncTooltip(this.series.chart.container, this.index);
                    }
                }
            }
        }
    },
    tooltip: {
        shared: true,
        valueDecimals: 2,
        crosshairs: true
    },
    xAxis: {
        type: 'datetime',
        crosshair: true,
        events: {
            setExtremes: syncExtremes
        }
    }
};
$("#ap_container").height("800px");
$("#ap_container").html(
'<div class="row"><div id="hc1" class="col-md-6">' +
'</div><div id="hc2" class="col-md-6"></div></div>' +
'<div class="row"><div id="hc3\" class="col-md-6"></div>' +
'<div id="hc4" class="col-md-6\"></div></div>');
$('<div class="chart">')
    .appendTo('#hc1')
    .highcharts({
        plotOptions: options.plotOptions,
        chart: {
            zoomType: 'x',
            marginLeft: 40, // Keep all charts left aligned
            spacingTop: 20,
            spacingBottom: 20
        },
        title: {
            text: 'Wind Speed',
            align: 'left',
            margin: 0,
            x: 30
        },
        credits: {
            enabled: false
        },
        legend: options.legend,
        xAxis: {
            type: 'datetime',
            crosshair: true,
            events: {
                setExtremes: syncExtremes
            }
        },
        yAxis: {
            title: {
                text: null
            }
        },
        tooltip: options.tooltip,
        series: ["""
        + series
        + """]
});
$('<div class="chart">')
    .appendTo('#hc2')
    .highcharts({
        plotOptions: options.plotOptions,
        chart: {
            zoomType: 'x',
            marginLeft: 40, // Keep all charts left aligned
            spacingTop: 20,
            spacingBottom: 20
        },
        title: {
            text: 'Air Temp',
            align: 'left',
            margin: 0,
            x: 30
        },
        credits: {
            enabled: false
        },
        legend: options.legend,
        xAxis: {
            type: 'datetime',
            crosshair: true,
            events: {
                setExtremes: syncExtremes
            }
        },
        yAxis: {
            title: {
                text: null
            }
        },
        tooltip: options.tooltip,
        series: ["""
        + series2
        + """]
});
$('<div class="chart">')
    .appendTo('#hc3')
    .highcharts({
        plotOptions: options.plotOptions,
        chart: {
            zoomType: 'x',
            marginLeft: 40, // Keep all charts left aligned
            spacingTop: 20,
            spacingBottom: 20
        },
        title: {
            text: 'RH',
            align: 'left',
            margin: 0,
            x: 30
        },
        credits: {
            enabled: false
        },
        legend: options.legend,
        xAxis: {
            type: 'datetime',
            crosshair: true,
            events: {
                setExtremes: syncExtremes
            }
        },
        yAxis: {
            title: {
                text: null
            }
        },
        tooltip: options.tooltip,
        series: ["""
        + series3
        + """]
});
$('<div class="chart">')
    .appendTo('#hc4')
    .highcharts({
        plotOptions: options.plotOptions,
        chart: {
            zoomType: 'x',
            marginLeft: 40, // Keep all charts left aligned
            spacingTop: 20,
            spacingBottom: 20
        },
        title: {
            text: 'Wind Direction',
            align: 'left',
            margin: 0,
            x: 30
        },
        credits: {
            enabled: false
        },
        legend: options.legend,
        xAxis: {
            type: 'datetime',
            crosshair: true,
            events: {
                setExtremes: syncExtremes
            }
        },
        yAxis: {
            title: {
                text: null
            }
        },
        tooltip: options.tooltip,
        series: ["""
        + series4
        + """]
});
    """
    )


def plotter(fdict):
    """Go"""
    ctx = get_context(fdict)

    (fig, [ax1, ax2, ax3, ax4]) = plt.subplots(
        4, 1, figsize=(12, 10), sharex=True
    )
    for height in [5, 10, 20, 40, 80, 120]:
        x = "_1" if height == 120 else ""
        ax1.plot(
            ctx["df"].index.values,
            ctx["df"]["airtc_%sm%s" % (height, x)].values,
            lw=2,
            label="%sm" % (height,),
        )
        ax2.plot(
            ctx["df"].index.values,
            ctx["df"]["rh_%sm%s" % (height, x)].values,
            lw=2,
            label="%sm" % (height,),
        )
        ax3.plot(
            ctx["df"].index.values,
            ctx["df"]["ws_%sm_s" % (height,)].values,
            lw=2,
            label="%sm" % (height,),
        )
        ax4.plot(
            ctx["df"].index.values,
            ctx["df"]["winddir_%sm_s" % (height,)].values,
            lw=2,
            label="%sm" % (height,),
        )
    ax1.legend(loc=(0.0, -0.15), ncol=6)
    ax1.grid(True)
    ax1.set_ylabel("Air Temp C")
    ax1.xaxis.set_major_formatter(
        mdates.DateFormatter(
            "%-I %p\n%-d %b", tz=pytz.timezone("America/Chicago")
        )
    )
    ax1.set_title(ctx["title"])
    ax2.grid(True)
    ax2.set_ylabel("RH %")
    ax3.grid(True)
    ax3.set_ylabel("Wind Speed mps")
    ax4.grid(True)
    ax4.set_ylabel("Wind Dir deg")
    # remove timezone since excel no likely
    ctx["df"].index = ctx["df"].index.tz_localize(None)
    return fig, ctx["df"]


if __name__ == "__main__":
    plotter(dict())
