import psycopg2
from pandas.io.sql import read_sql
import datetime
import numpy as np
from pyiem.plot import MapPlot

PDICT = {'state': 'State Level Maps (select state)',
         'midwest': 'Midwest Map'}
PDICT2 = {'both': 'Show both contour and values',
          'values': 'Show just the values',
          'contour': 'Show just the contour'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This map produces an analysis of change in
    the number of days for the growing season."""
    d['arguments'] = [
        dict(type='select', name='sector', default='state',
             options=PDICT, label='Select Map Region'),
        dict(type='clstate', name='state', default='IA',
             label='Select State to Plot (when appropriate)'),
        dict(type='select', name='opt', options=PDICT2, default='both',
             label='Map Plot/Contour View Option'),
        dict(type='year', name='p1syear', default=1951,
             label='Start Year (inclusive) of Period One:'),
        dict(type='year', name='p1eyear', default=1980,
             label='End Year (inclusive) of Period One:'),
        dict(type='year', name='p2syear', default=1981,
             label='Start Year (inclusive) of Period Two:'),
        dict(type='year', name='p2eyear', default=2010,
             label='End Year (inclusive) of Period Two:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    state = fdict.get('state', 'IA')[:2]
    sector = fdict.get('sector', 'state')
    opt = fdict.get('opt', 'both')
    p1syear = int(fdict.get('p1syear', 1951))
    p1eyear = int(fdict.get('p1eyear', 1980))
    p2syear = int(fdict.get('p2syear', 1981))
    p2eyear = int(fdict.get('p2eyear', 2010))

    table = "alldata"
    if sector == 'state':
        table = "alldata_%s" % (state, )

    df = read_sql("""
    WITH season1 as (
        SELECT station, year,
        min(case when month > 7 and low < 32 then
            extract(doy from day) else 366 end) as first_freeze,
        max(case when month < 7 and low < 32 then
            extract(doy from day) else 0 end) as last_freeze
        from """ + table + """ WHERE
        year >= %s and year <= %s GROUP by station, year),
    season2 as (
        SELECT station, year,
        min(case when month > 7 and low < 32 then
            extract(doy from day) else 366 end) as first_freeze,
        max(case when month < 7 and low < 32 then
            extract(doy from day) else 0 end) as last_freeze
        from """ + table + """ WHERE
        year >= %s and year <= %s GROUP by station, year),
    agg as (
        SELECT p1.station, avg(p1.first_freeze) as p1_first_fall,
        avg(p1.last_freeze) as p1_last_spring,
        avg(p2.first_freeze) as p2_first_fall,
        avg(p2.last_freeze) as p2_last_spring
        from season1 as p1 JOIN season2 as p2 on (p1.station = p2.station)
        GROUP by p1.station)

    SELECT station, ST_X(geom) as lon, ST_Y(geom) as lat,
    d.* from agg d JOIN stations t ON (d.station = t.id)
    WHERE t.network in ('IACLIMATE', 'NDCLIMATE', 'SDCLIMATE', 'NECLIMATE',
    'KSCLIMATE', 'MOCLIMATE', 'ILCLIMATE', 'WICLIMATE', 'MNCLIMATE',
    'MICLIMATE', 'INCLIMATE', 'OHCLIMATE', 'KYCLIMATE')
    and substr(station, 3, 1) != 'C' and substr(station, 3, 4) != '0000'
    """, pgconn, params=[p1syear, p1eyear,
                         p2syear, p2eyear],
                  index_col=None)
    df['p1_season'] = df['p1_first_fall'] - df['p1_last_spring']
    df['p2_season'] = df['p2_first_fall'] - df['p2_last_spring']
    df['season_delta'] = df['p2_season'] - df['p1_season']
    # Reindex so that most extreme values are first
    df = df.reindex(df['season_delta'].abs().sort_values(
                                                ascending=False).index)

    title = 'Number of Days in Growing Season '
    m = MapPlot(sector=sector, state=state, axisbg='white',
                title=('%.0f-%.0f minus %.0f-%.0f %s Difference'
                       ) % (p2syear, p2eyear, p1syear, p2eyear, title),
                subtitle=('based on IEM Archives'),
                titlefontsize=14)
    # Create 9 levels centered on zero
    abval = df['season_delta'].abs().max()
    levels = np.linspace(0 - abval, abval, 9)
    levels = [round(x, 1) for x in levels]
    if opt in ['both', 'contour']:
        m.contourf(df['lon'].values, df['lat'].values,
                   df['season_delta'].values, levels,
                   cmap=plt.get_cmap('seismic'),
                   units='days')
    if sector == 'state':
        m.drawcounties()
    if opt in ['both', 'values']:
        m.plot_values(df['lon'].values, df['lat'].values,
                      df['season_delta'].values,
                      fmt='%.1f')

    return m.fig, df

if __name__ == '__main__':
    plotter(dict(over='annual'))
