"""Spatial Frequencies"""
import datetime

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context
from pyiem.network import Table as NetworkTable
import psycopg2


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This plot shows the percentage of years
    that one station had a larger total than a given station.
    """
    today = datetime.date.today()
    desc['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:', network='IACLIMATE'),
        dict(type="year", name="year", default=today.year,
             label="Year to Compare:"),
        ]
    return desc


def plotter(fdict):
    """ Go """
    from pyiem.plot.geoplot import MapPlot
    import matplotlib.pyplot as plt
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    nt = NetworkTable(ctx['network'])
    year = ctx['year']

    dbconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    table = "alldata_%s" % (station[:2], )
    df = read_sql("""
    with yearly as (
        select year, sum(precip), station from alldata_ia
        where precip is not null and sday < '1012' GROUP by station, year),
    ames as (
        select year, sum from yearly where station = %s),
    combo as (
        select y.year, y.station, y.sum as other, a.sum as ames
        from yearly y JOIN ames a on (y.year = a.year)
        WHERE y.station != %s and y.station != 'IA0807'),
    y2017 as (
        select * from combo where year = 2017),
    agg as (
        SELECT station, st_x(geom) as lon, st_y(geom) as lat,
        sum(case when other > ames then 1 else 0 end) as hits, count(*)
        from combo c JOIN stations t on (c.station = t.id)
        WHERE t.network = %s and c.year < 2017
        GROUP by station, lon, lat)
    SELECT y.ames as ames, y.other as other, a.* from
    y2017 y JOIN agg a on (y.station = a.station)
     """, dbconn, params=(station, station, ctx['network']),
                  index_col='station')
    df = df[df['count'] > 50]
    df['h2017'] = 'red'
    df.loc[df['other'] > df['ames'], 'h2017'] = 'blue'
    df['freq'] = df['hits'] / df['count'] * 100.
    df.sort_values('freq', inplace=True)

    mp = MapPlot(continentalcolor='white',
                 title=('Percentage of Years with Higher Precipitation Total '
                        'than Ames'),
                 subtitle=('For 1 January thru 12 October Period, sites '
                           'in blue are higher for 2017'))
    mp.plot_values(df['lon'].values, df['lat'].values, df['freq'].values,
                   '%.0f', labelbuffer=1, color=df['h2017'].values)
    #mp.contourf(df['lon'].values, df['lat'].values, df['freq'].values,
    #            range(0, 101, 10), cmap=plt.get_cmap('plasma_r'))
    mp.drawcounties()
    return mp.fig, df


if __name__ == '__main__':
    plotter(dict())
