import psycopg2
import datetime
import pandas as pd
from collections import OrderedDict
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql

PDICT = OrderedDict([(0, 'Include calm observations'),
                     (2, 'Include only non-calm observations >= 2kt'),
                     (5, 'Include only non-calm observations >= 5kt'),
                     ])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['highcharts'] = True
    d['cache'] = 86400
    d['description'] = """This plot displays the number of accumulated
    hours below a given wind chill temperature threshold by season. The
    labeled season shown is for the year of January. So the season of 2016
    would be from July 2015 to June 2016.  Hours with no wind are included
    in this analysis with the wind chill temperature being the air temperature
    in those instances.
    """
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
        dict(type='year', name='season', default=datetime.datetime.now().year,
             label='Select Season to Highlight'),
        dict(type='select', name='wind', default=0, options=PDICT,
             label='Include Calm Observations? (wind threshold)'),
    ]
    return d


def highcharts(fdict):
    """ Do highcharts """
    ctx = get_context(fdict)
    s = ""
    if 'season' in ctx['lines']:
        s = """{
        name: '"""+str(ctx['season'])+"""',
        type: 'line',
        marker: {
            lineWidth: 2,
            lineColor: '"""+ctx['lines']['season']['c']+"""'
        },
        data: """+str([list(a) for a in zip(ctx['lines']['season']['x'],
                                            ctx['lines']['season']['y'])])+"""

        },"""
    return """
$("#ap_container").highcharts({
    title: {text: '""" + ctx['title'] + """'},
    subtitle: {text: '""" + ctx['subtitle'] + """'},
    chart: {zoomType: 'x'},
    tooltip: {
        shared: true,
        valueDecimals: 2,
        valueSuffix: ' days',
        headerFormat: '<span style="font-size: 10px">Wind Chill &lt;= {point.key} F</span><br/>'
    },
    xAxis: {title: {text: 'Wind Chill Temperature (F)'}},
    yAxis: {title: {text: 'Total Time Hours [expressed in days]'}},
    series: ["""+s+"""{
        name: '25%',
        type: 'line',
        marker: {
            lineWidth: 2,
            lineColor: '"""+ctx['lines']['25%']['c']+"""'
        },
        data: """+str([list(a) for a in zip(ctx['lines']['25%']['x'],
                                            ctx['lines']['25%']['y'])])+"""
        },{
        name: 'Avg',
        type: 'line',
        marker: {
            lineWidth: 2,
            lineColor: '"""+ctx['lines']['mean']['c']+"""'
        },
        data: """+str([list(a) for a in zip(ctx['lines']['mean']['x'],
                                            ctx['lines']['mean']['y'])])+"""
        },{
        name: '75%',
        type: 'line',
        marker: {
            lineWidth: 2,
            lineColor: '"""+ctx['lines']['75%']['c']+"""'
        },
        data: """+str([list(a) for a in zip(ctx['lines']['75%']['x'],
                                            ctx['lines']['75%']['y'])])+"""
        },{
        name: 'Max',
        type: 'line',
        marker: {
            lineWidth: 2,
            lineColor: '"""+ctx['lines']['max']['c']+"""'
        },
        data: """+str([list(a) for a in zip(ctx['lines']['max']['x'],
                                            ctx['lines']['max']['y'])])+"""
        }]
});
    """


def get_context(fdict):
    """ Get the data"""
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    sknt = int(fdict.get('wind', 0))
    nt = NetworkTable(network)
    df = read_sql("""WITH data as (
        SELECT valid, lag(valid) OVER (ORDER by valid ASC),
        extract(year from valid + '5 months'::interval) as season,
        wcht(tmpf::numeric, (sknt * 1.15)::numeric) from alldata
        WHERE station = %s and tmpf is not null and sknt is not null
        and tmpf < 50 and sknt >= %s ORDER by valid)
    SELECT case when (valid - lag) < '3 hours'::interval then (valid - lag)
    else '3 hours'::interval end as timedelta, wcht,
    season from data
    """, pgconn, params=(station, sknt), index_col=None)

    df2 = pd.DataFrame()
    for i in range(32, -51, -1):
        df2[i] = df[df['wcht'] < i].groupby('season')['timedelta'].sum()
        df2[i] = df[df['wcht'] < i].groupby('season')['timedelta'].sum()
    df2.fillna(0, inplace=True)
    ctx = {}
    ctx['df'] = df2
    ctx['title'] = ("[%s] %s Wind Chill Hours"
                    ) % (station, nt.sts[station]['name'])
    ctx['subtitle'] = ("Hours below threshold by season (wind >= %.0f kts)"
                       ) % (sknt,)
    ctx['dfdescribe'] = df2.iloc[:-1].describe()
    ctx['season'] = int(fdict.get('season', datetime.datetime.now().year))
    ctx['lines'] = {}

    if ctx['season'] in ctx['df'].index.values:
        s = ctx['df'].loc[[ctx['season']]].transpose()
        s = s.dropna().astype('timedelta64[h]')
        ctx['lines']['season'] = {
            'x': s.index.values[::-1],
            'y': s[ctx['season']].values[::-1] / 24.,
            'c': 'blue',
            'label': str(ctx['season'])}

    lbls = ['25%', 'mean', '75%', 'max']
    colors = ['g', 'k', 'r', 'orange']
    for color, lbl in zip(colors, lbls):
        s = ctx['dfdescribe'].loc[[lbl]].transpose()
        s = s.dropna().astype('timedelta64[h]')
        ctx['lines'][lbl] = {
            'x': s.index.values[::-1],
            'y': s[lbl].values[::-1] / 24.,
            'label': lbl,
            'c': color
        }

    return ctx


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ctx = get_context(fdict)

    (fig, ax) = plt.subplots(1, 1)
    for year in ctx['df'].index.values:
        s = ctx['df'].loc[[year]].transpose()
        s = s.dropna().astype('timedelta64[h]')
        ax.plot(s.index.values, s[year].values / 24., c='tan')
    if 'season' in ctx['lines']:
        ax.plot(ctx['lines']['season']['x'], ctx['lines']['season']['y'],
                c=ctx['lines']['season']['c'],
                zorder=5, label=ctx['lines']['season']['label'], lw=2)
    for lbl in ['25%', 'mean', '75%']:
        ax.plot(ctx['lines'][lbl]['x'], ctx['lines'][lbl]['y'],
                c=ctx['lines'][lbl]['c'], zorder=2,
                label=ctx['lines'][lbl]['label'], lw=2)
    ax.legend(loc=2)
    ax.grid(True)
    ax.set_xlim(-50, 32)
    ax.set_xlabel("Wind Chill Temperature $^\circ$F")
    ax.set_ylabel("Total Time Hours [expressed in days]")
    ax.set_title("%s\n%s" % (ctx['title'], ctx['subtitle']))
    return fig, ctx['df']


if __name__ == '__main__':
    plotter(dict())
