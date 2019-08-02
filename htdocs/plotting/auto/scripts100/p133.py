"""snowfall totals around day"""
import datetime

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['highcharts'] = True
    desc['cache'] = 86400
    desc['description'] = """This plot displays the total reported snowfall for
    a period prior to a given date and then after the date for the winter
    season.  When you select a date to split the winter season, the year
    shown in the date can be ignored.
    """
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station:', network='IACLIMATE'),
        dict(type='date', name='date', default='2015/12/25', min='2015/01/01',
             label='Split Season by Date: (ignore the year)'),
    ]
    return desc


def get_data(fdict):
    """ Get the data"""
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    date = ctx['date']
    jul1 = datetime.date(date.year if date.month > 6 else date.year - 1, 7, 1)
    offset = int((date - jul1).days)
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
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    date = ctx['date']
    df = get_data(fdict)

    j = dict()
    j['title'] = {'text': '%s [%s] Snowfall Totals' % (
        ctx['_nt'].sts[station]['name'], station)}
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
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    date = ctx['date']
    df = get_data(fdict)
    if df.empty:
        raise NoDataFound('Error, no results returned!')

    (fig, ax) = plt.subplots(1, 1)
    ax.scatter(df['before'].values, df['after'].values)
    ax.set_xlim(left=-0.1)
    ax.set_ylim(bottom=-0.1)
    ax.set_xlabel("Snowfall Total [inch] Prior to %s" % (
        date.strftime("%-d %b"), ))
    ax.set_ylabel("Snowfall Total [inch] On and After %s" % (
        date.strftime("%-d %b"), ))
    ax.grid(True)
    ax.set_title(("%s [%s] Snowfall Totals\nPrior to and after: %s"
                  ) % (ctx['_nt'].sts[station]['name'], station,
                       date.strftime("%-d %B")))
    ax.axvline(df['before'].mean(), color='r', lw=2,
               label='Before Avg: %.1f' % (df['before'].mean(),))
    ax.axhline(df['after'].mean(), color='b', lw=2,
               label='After Avg: %.1f' % (df['after'].mean(),))
    ax.legend(ncol=2, fontsize=12)
    return fig, df


if __name__ == '__main__':
    plotter(dict())
