"""Accumuldated days"""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = OrderedDict([('high_above', 'High Temperature At or Above'),
                     ('high_below', 'High Temperature Below'),
                     ('low_above', 'Low Temperature At or Above'),
                     ('low_below', 'Low Temperature Below')])
PDICT2 = OrderedDict([('jan1', 'January 1'),
                      ('jul1', 'July 1')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['highcharts'] = True
    desc['description'] = """This plot displays the accumulated number of days
    that the high or low temperature was above or below some threshold.
    """
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station:', network='IACLIMATE'),
        dict(type='select', name='var', default='high_above',
             label='Which Metric', options=PDICT),
        dict(type="int", name="threshold", default=32,
             label='Threshold (F)'),
        dict(type="select", name='split', default='jan1',
             options=PDICT2, label='Where to split the year?'),
        dict(type='year', name='year', default=datetime.date.today().year,
             label='Year to Highlight in Chart'),
    ]
    return desc


def highcharts(fdict):
    """ Highcharts Output """
    station = fdict.get('station', 'IATDSM')
    network = fdict.get('network', 'IACLIMATE')
    varname = fdict.get('var', 'high_above')
    nt = NetworkTable(network)
    df = get_data(fdict, nt)

    j = dict()
    j['tooltip'] = {
        'shared': True,
        'headerFormat':
            '<span style="font-size: 10px">{point.key: %b %e}</span><br/>'}
    j['title'] = {'text': '%s [%s] %s %sF' % (nt.sts[station]['name'],
                                              station,
                                              PDICT[varname],
                                              int(fdict.get('threshold', 32)))}
    j['yAxis'] = {'title': {'text': 'Accumulated Days'}, 'startOnTick': False}
    j['xAxis'] = {
            'type': 'datetime',
            'dateTimeLabelFormats': {  # don't display the dummy year
                'month': '%e. %b',
                'year': '%b'
            },
            'title': {
                'text': 'Date'
            }
    }
    j['chart'] = {'zoomType': 'xy', 'type': 'line'}
    avgs = []
    ranges = []
    thisyear = []
    for doy, row in df.iterrows():
        ts = datetime.date(2001, 1, 1) + datetime.timedelta(days=(doy - 1))
        ticks = (ts - datetime.date(1970, 1, 1)).total_seconds() * 1000.
        avgs.append([ticks, row['avg']])
        ranges.append([ticks, row['min'], row['max']])
        if row['thisyear'] >= 0:
            thisyear.append([ticks, row['thisyear']])
    lbl = ("%s" % (fdict.get('year', 2015),)
           if fdict.get('split', 'jan1') == 'jan1'
           else "%s - %s" % (int(fdict.get('year', 2015)) - 1,
                             int(fdict.get('year', 2015))))
    j['series'] = [{
            'name': 'Average', 'data': avgs, 'zIndex': 1,
            'tooltip': {'valueDecimals': 2},
            'marker': {
                'fillColor': 'white',
                'lineWidth': 2,
                'lineColor': 'red'
            }
        }, {
            'name': lbl, 'data': thisyear,
            'zIndex': 1,
            'marker': {
                'fillColor': 'blue',
                'lineWidth': 2,
                'lineColor': 'green'
            }
        }, {
            'name': 'Range',
            'data': ranges,
            'type': 'arearange',
            'lineWidth': 0,
            'linkedTo': ':previous',
            'color': 'tan',
            'fillOpacity': 0.3,
            'zIndex': 0
        }]
    return j


def get_data(fdict, nt):
    """ Get the data"""
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    threshold = ctx['threshold']
    varname = ctx['var']
    year = ctx['year']
    split = ctx['split']
    table = "alldata_%s" % (station[:2], )
    days = 0 if split == 'jan1' else 183
    opp = " < " if varname.find("_below") > 0 else ' >= '
    col = "high" if varname.find("high") == 0 else "low"
    # We need to do some magic to compute the start date, since we don't want
    # an incomplete year mucking things up
    sts = nt.sts[station]['archive_begin']
    if sts.month > 1:
        sts = sts + datetime.timedelta(days=365)
        sts = sts.replace(month=1, day=1)
    if split == 'jul1':
        sts = sts.replace(month=7, day=1)
    df = read_sql("""
    with data as (
        select extract(year from day + '%s days'::interval) as season,
        extract(doy from day + '%s days'::interval) as doy,
        (case when """+col+""" """+opp+""" %s then 1 else 0 end) as hit
        from """+table+"""
        where station = %s and day >= %s),
    agg1 as (
        SELECT season, doy,
        sum(hit) OVER (PARTITION by season ORDER by doy ASC) from data)
    SELECT doy - %s as doy, min(sum), avg(sum), max(sum),
    max(case when season = %s then sum else null end) as thisyear from agg1
    WHERE doy < 365 GROUP by doy ORDER by doy ASC
    """, pgconn, params=(days, days, threshold, station, sts, days, year),
                  index_col=None)
    df['datestr'] = df['doy'].apply(lambda x: (datetime.date(2001, 1, 1) +
                                               datetime.timedelta(days=x)
                                               ).strftime("%-d %b"))
    df.set_index('doy', inplace=True)
    return df


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    threshold = ctx['threshold']
    varname = ctx['var']
    year = ctx['year']
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)
    df = get_data(fdict, nt)
    if df.empty:
        raise ValueError('Error, no results returned!')

    (fig, ax) = plt.subplots(1, 1)
    ax.plot(df.index.values, df['avg'], c='k', lw=2, label='Average')
    ax.plot(df.index.values, df['thisyear'], c='g', lw=2, label="%s" % (year,))
    ax.plot(df.index.values, df['max'], c='r', lw=2, label='Max')
    ax.plot(df.index.values, df['min'], c='b', lw=2, label='Min')
    ax.set_title((r"%s [%s]\n%s %.0f$^\circ$F"
                  ) % (nt.sts[station]['name'], station, PDICT[varname],
                       threshold))
    ax.legend(ncol=1, loc=2)
    xticks = []
    xticklabels = []
    for x in range(int(df.index.min()) - 1, int(df.index.max()) + 1):
        ts = datetime.date(2000, 1, 1) + datetime.timedelta(days=x)
        if ts.day == 1:
            xticks.append(x)
            xticklabels.append(ts.strftime("%b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.grid(True)
    ax.set_xlim(int(df.index.min()) - 1, int(df.index.max()) + 1)
    ax.set_ylabel("Accumulated Days")
    return fig, df


if __name__ == '__main__':
    plotter(dict())
