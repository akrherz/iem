import psycopg2
from pandas.io.sql import read_sql
import datetime
import numpy as np
from pyiem.plot import MapPlot
import calendar

PDICT = {'state': 'State Level Maps (select state)',
         'midwest': 'Midwest Map'}
PDICT2 = {'both': 'Show both contour and values',
          'values': 'Show just the values',
          'contour': 'Show just the contour'}
PDICT3 = {'total_precip': 'Total Precipitation',
          'avg_temp': 'Average Temperature',
          'avg_high': 'Average High Temperature',
          'avg_low': 'Average Low Temperature'}
UNITS = {'total_precip': 'inch',
         'avg_temp': 'F',
         'avg_high': 'F',
         'avg_low': 'F'}
PRECISION = {'total_precip': 2,
             'avg_temp': 1,
             'avg_high': 1,
             'avg_low': 1}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This application produces map analysis of
    climatological averages."""
    d['arguments'] = [
        dict(type='select', name='sector', default='state',
             options=PDICT, label='Select Map Region'),
        dict(type='clstate', name='state', default='IA',
             label='Select State to Plot (when appropriate)'),
        dict(type='month', name='month', default=datetime.date.today().month,
             label='Select Month (when appropriate)'),
        dict(type='select', name='opt', options=PDICT2, default='both',
             label='Map Plot/Contour View Option'),
        dict(type='select', name='var', options=PDICT3, default='total_precip',
             label='Which Variable to Plot'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    state = fdict.get('state', 'IA')[:2]
    varname = fdict.get('var', 'total_precip')
    sector = fdict.get('sector', 'state')
    opt = fdict.get('opt', 'both')
    month = int(fdict.get('month', datetime.date.today().month))

    df = read_sql("""
    WITH data as (
        SELECT station, extract(month from valid) as month,
        sum(precip) as total_precip, avg(high) as avg_high,
        avg(low) as avg_low, avg((high+low)/2.) as avg_temp
        from ncdc_climate81 GROUP by station, month)

    SELECT station, ST_X(geom) as lon, ST_Y(geom) as lat, month,
    total_precip, avg_high, avg_low, avg_temp from data d JOIN stations t
    ON (d.station = t.id) WHERE t.network = 'NCDC81' and
    t.state in ('IA', 'ND', 'SD', 'NE', 'KS', 'MO', 'IL', 'WI', 'MN', 'MI',
    'IN', 'OH', 'KY')
    """, pgconn, index_col=None)

    df2 = df[df['month'] == month]
    title = "%s" % (PDICT3[varname], )
    m = MapPlot(sector=sector, state=state, axisbg='white',
                title=('NCEI 1981-2010 Climatology of %s %s'
                       ) % (calendar.month_name[month], title),
                subtitle=('based on National Centers for '
                          'Environmental Information (NCEI) 1981-2010'
                          ' Climatology'))
    levels = np.linspace(df2[varname].min(), df2[varname].max(), 10)
    levels = [round(x, PRECISION[varname]) for x in levels]
    if opt in ['both', 'contour']:
        m.contourf(df2['lon'].values, df2['lat'].values,
                   df2[varname].values, levels, units=UNITS[varname])
    if sector == 'state':
        m.drawcounties()
    if opt in ['both', 'values']:
        m.plot_values(df2['lon'].values, df2['lat'].values,
                      df2[varname].values,
                      fmt='%%.%if' % (PRECISION[varname],))

    return m.fig, df

if __name__ == '__main__':
    plotter(dict())
