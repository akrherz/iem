"""talltowers plot"""
import datetime

import psycopg2
import numpy as np
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context

PDICT = {'above': 'Above Threshold',
         'below': 'Below Threshold'}
PDICT2 = {'max_rh': 'Daily Max RH',
          'min_rh': 'Daily Min RH'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['highcharts'] = True
    desc['description'] = """ WORK-IN-PROGRESS! """
    desc['arguments'] = [
        dict(type='networkselect', name='station', default='ETTI4',
             label='Select Station', network='TALLTOWERS'),
        dict(type='datetime', name='dt', default="2016/09/15 2340",
             label='Start Time (UTC Time Zone):', min="2016/04/01 0000"),
        dict(type='int', name='minutes', default=10,
             label='Number of Minutes to Plot')
                      ]
    return desc


def get_context(fdict):
    pgconn = psycopg2.connect(database='talltowers',
                              host='talltowers-db.local', user='tt_web')
    ctx = get_autoplot_context(fdict, get_description())
    dt = ctx['dt']
    station = ctx['station']
    minutes = ctx['minutes']
    nt = NetworkTable("TALLTOWERS")
    towerid = nt.sts[station]['remote_id']

    ctx['df'] = read_sql("""
    SELECT * from data_analog where tower = %s and
    valid between %s and %s ORDER by valid ASC
    """, pgconn, params=(towerid, dt,
                         dt + datetime.timedelta(minutes=minutes)),
                         index_col='valid')
    return ctx


def highcharts(fdict):
    ctx = get_context(fdict)
    df = ctx['df']
    df['ticks'] = df.index.values.astype(np.int64) // 10 ** 6
    lines = []
    lines2 = []
    lines3 = []
    lines4 = []
    for col in ['ws_5m_s', 'ws_5m_nw', "ws_10m_s", "ws_10m_nwht",
                "ws_20m_s", "ws_20m_nw", "ws_40m_s", "ws_40m_nwht",
                "ws_80m_s", "ws_80m_nw", "ws_120m_s", "ws_120m_nwht"]:
        v = df[['ticks', col]].to_json(orient='values')
        lines.append("""{
            name: '""" + col + """',
            type: 'line',
            tooltip: {valueDecimal: 1},
            data: """+v+"""
            }
        """)
    for col in ['airtc_5m', 'airtc_10m', 'airtc_20m', 'airtc_40m',
                'airtc_80m', 'airtc_120m_1', 'airtc_120m_2']:
        v = df[['ticks', col]].to_json(orient='values')
        lines2.append("""{
            name: '""" + col + """',
            type: 'line',
            tooltip: {valueDecimal: 1},
            data: """+v+"""
            }
        """)
    for col in ['rh_5m', 'rh_10m', 'rh_20m', 'rh_40m',
                'rh_80m', 'rh_120m_1', 'rh_120m_2']:
        v = df[['ticks', col]].to_json(orient='values')
        lines3.append("""{
            name: '""" + col + """',
            type: 'line',
            tooltip: {valueDecimal: 1},
            data: """+v+"""
            }
        """)
    for col in ['winddir_5m_s', 'winddir_5m_nw', 'winddir_10m_s',
                'winddir_10m_nw', 'winddir_20m_s', 'winddir_20m_nw',
                'winddir_40m_s', 'winddir_40m_nw', 'winddir_80m_s',
                'winddir_80m_nw', 'winddir_120m_s', 'winddir_120m_nw']:
        v = df[['ticks', col]].to_json(orient='values')
        lines4.append("""{
            name: '""" + col + """',
            type: 'line',
            tooltip: {valueDecimal: 1},
            data: """+v+"""
            }
        """)

    series = ",".join(lines)
    series2 = ",".join(lines2)
    series3 = ",".join(lines3)
    series4 = ",".join(lines4)

    return """
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
    global: {useUTC: false},
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
        series: [""" + series + """]
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
        series: [""" + series2 + """]
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
        series: [""" + series3 + """]
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
        series: [""" + series4 + """]
});
    """


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ctx = get_context(fdict)

    (fig, ax) = plt.subplots(1, 1)
    for height in [5, 10, 20, 40, 80, 120]:
        x = "_1" if height == 120 else ''
        ax.plot(ctx['df'].index.values,
                ctx['df']['airtc_%sm%s' % (height, x)].values, lw=2,
                label='%sm' % (height,))
    ax.legend(loc='best')
    ax.grid(True)
    # remove timezone since excel no likely
    ctx['df'].index = ctx['df'].index.tz_localize(None)
    return fig, ctx['df']


if __name__ == '__main__':
    plotter(dict())
