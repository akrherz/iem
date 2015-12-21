import psycopg2
import datetime
import calendar
from collections import OrderedDict
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['highcharts'] = True
    d['cache'] = 86400
    d['description'] = """This plot displays the total reported snowfall for
    a period prior to a given date and then after the date for the winter
    season.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='date', name='date', default='2015/12/25', min='2015/01/01',
             label='Split Season by Date: (ignore the year)'),
    ]
    return d


def get_data(fdict):
    """ Get the data"""
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA2203')
    network = fdict.get('network', 'IACLIMATE')
    date = datetime.datetime.strptime(fdict.get('date', '2015-12-25'),
                                      '%Y-%m-%d')
    jul1 = datetime.date(date.year if date.month > 6 else date.year - 1, 7, 1)
    offset = int((date.date() - jul1).days)
    table = "alldata_%s" % (station[:2],)
    df = read_sql("""
    with obs as (
        select day,
        day -
        ((case when month > 6 then year else year - 1 end)||'-07-01')::date
        as doy,
        (case when month > 6 then year else year - 1 end) as eyear, snow
        from """+table+""" where station = %s)

        SELECT eyear, sum(case when doy < %s then snow else 0 end) as before,
        sum(case when doy >= %s then snow else 0 end) as after,
        sum(snow) as total from obs
        GROUP by eyear ORDER by eyear ASC
    """, pgconn, params=(station, offset, offset), index_col='eyear')
    df = df[df['total'] > 0]
    return df


def highcharts(fdict):
    """ Highcharts Output """
    station = fdict.get('station', 'IA2203')
    network = fdict.get('network', 'IACLIMATE')
    nt = NetworkTable(network)
    date = datetime.datetime.strptime(fdict.get('date', '2015-12-25'),
                                      '%Y-%m-%d')
    df = get_data(fdict)

    j = dict()
    j['title'] = {'text': '%s [%s] Snowfall Totals' % (nt.sts[station]['name'],
                                                       station)}
    j['subtitle'] = {'text': 'Before and After %s' % (date.strftime("%-d %B"),)
                     }
    j['xAxis'] = {'title': {'text': 'Snowfall Total [inch] before %s' % (
                        date.strftime("%-d %B"),)},
                  'plotLines': [{'color': 'red',
                                 'value': df['before'].mean(),
                                 'width': 1,
                                 'label': {
                                    'text': '%.1fin' % (df['before'].mean(),)},
                                 'zindex': 2}]}
    j['yAxis'] = {'title': {'text': 'Snowfall Total [inch] on or after %s' % (
                        date.strftime("%-d %B"),)},
                  'plotLines': [{'color': 'red',
                                 'value': df['after'].mean(),
                                 'width': 1,
                                 'label': {
                                    'text': '%.1fin' % (df['after'].mean(),)},
                                 'zindex': 2}]}
    j['chart'] = {'zoomType': 'xy', 'type': 'scatter'}
    rows = []
    for yr, row in df.iterrows():
        rows.append(dict(x=round(row['before'], 2), y=round(row['after'], 2),
                         name="%s-%s" % (yr, yr+1)))
    j['series'] = [{'data': rows,
                    'tooltip': {
                        'headerFormat': '',
                        'pointFormat': ('<b>Season:</b> {point.name}<br />'
                                        'Before: {point.x} inch<br />'
                                        'After: {point.y} inch')}
                    }]
    return j


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    station = fdict.get('station', 'IA2203')
    network = fdict.get('network', 'IACLIMATE')
    nt = NetworkTable(network)
    date = datetime.datetime.strptime(fdict.get('date', '2015-12-25'),
                                      '%Y-%m-%d')
    df = get_data(fdict)
    if len(df.index) == 0:
        return 'Error, no results returned!'

    (fig, ax) = plt.subplots(1, 1)
    ax.scatter(df['before'], df['after'])
    ax.set_xlim(left=-0.1)
    ax.set_ylim(bottom=-0.1)
    ax.set_xlabel("Snowfall Total [inch] Prior to %s" % (
        date.strftime("%-d %b"), ))
    ax.set_ylabel("Snowfall Total [inch] On and After %s" % (
        date.strftime("%-d %b"), ))
    ax.grid(True)
    ax.set_title(("%s [%s] Snowfall Totals\nPrior to and after: %s"
                  ) % (nt.sts[station]['name'], station,
                       date.strftime("%-d %B")))
    ax.axvline(df['before'].mean(), color='r',
               label='Before Avg: %.1f' % (df['before'].mean(),))
    ax.axhline(df['after'].mean(), color='r',
               label='After Avg: %.1f' % (df['after'].mean(),))
    ax.legend(ncol=2, fontsize=12)
    return fig, df
