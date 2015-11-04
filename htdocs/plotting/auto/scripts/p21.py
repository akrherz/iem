import psycopg2
import datetime
import numpy as np
from pandas.io.sql import read_sql

PDICT = {'high': 'High temperature',
         'low': 'Low Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This map displays an analysis of the change in
    average high or low temperature over a time period of your choice."""
    today = datetime.date.today()
    threeweeks = today - datetime.timedelta(days=21)
    d['arguments'] = [
        dict(type='date', name='date1',
             default=threeweeks.strftime("%Y/%m/%d"),
             label='From Date (ignore year):',
             min="2014/01/01"),  # Comes back to python as yyyy-mm-dd
        dict(type='date', name='date2', default=today.strftime("%Y/%m/%d"),
             label='To Date (ignore year):',
             min="2014/01/01"),  # Comes back to python as yyyy-mm-dd
        dict(type='select', name='varname', default='high',
             label='Which metric to plot?', options=PDICT),

    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    import matplotlib.cm as cm
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    date1 = datetime.datetime.strptime(fdict.get('date1', '2014-09-01'),
                                       '%Y-%m-%d')
    date2 = datetime.datetime.strptime(fdict.get('date2', '2014-09-22'),
                                       '%Y-%m-%d')
    date1 = date1.replace(year=2000)
    date2 = date2.replace(year=2000)

    varname = fdict.get('varname', 'low')

    df = read_sql("""
    WITH t2 as (
         SELECT station, high, low from ncdc_climate81 WHERE
         valid = %s
    ), t1 as (
        SELECT station, high, low from ncdc_climate81 where
        valid = %s
    ), data as (
        SELECT t2.station, t1.high as t1_high, t2.high as t2_high,
        t1.low as t1_low, t2.low as t2_low from t1 JOIN t2 on
        (t1.station = t2.station)
    )
    SELECT d.station, ST_x(geom) as lon, ST_y(geom) as lat,
    t2_high -  t1_high as high, t2_low - t1_low as low from data d JOIN
    stations s on (s.id = d.station) where s.network = 'NCDC81'
    and s.state not in ('HI', 'AK')
    """, pgconn, params=(date2, date1), index_col='station')

    days = int((date2 - date1).days)
    extent = int(df[varname].abs().max())
    m = MapPlot(sector='conus',
                title=('%s Day Change in %s NCDC 81 Climatology'
                       ) % (days, PDICT[varname]),
                subtitle='from %s to %s' % (date1.strftime("%-d %B"),
                                            date2.strftime("%-d %B"))
                )
    cmap = cm.get_cmap("RdBu_r")
    m.contourf(df['lon'].values, df['lat'].values, df[varname].values,
               np.arange(0-extent, extent+1, 2), cmap=cmap, units='F')

    return m.fig, df
