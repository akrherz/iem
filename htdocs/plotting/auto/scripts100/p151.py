import psycopg2
from pandas.io.sql import read_sql
import datetime
import numpy as np
from pyiem.plot import MapPlot, centered_bins
from collections import OrderedDict

PDICT = {'state': 'State Level Maps (select state)',
         'midwest': 'Midwest Map'}
PDICT2 = {'both': 'Show both contour and values',
          'values': 'Show just the values',
          'contour': 'Show just the contour'}
PDICT3 = OrderedDict([
        ('total_precip', 'Total Precipitation'),
        ('gdd', 'Growing Degree Days (base=50/86)'),
        ('sdd', 'Stress Degree Days (High > 86)'),
        ('avg_temp', 'Average Temperature'),
        ('avg_high', 'Average High Temperature'),
        ('avg_low', 'Average Low Temperature'),
        ('days_high_above', 'Days with High Temp At or Above [Threshold]')])
UNITS = {'total_precip': 'inch',
         'gdd': 'F',
         'sdd': 'F',
         'avg_temp': 'F',
         'avg_high': 'F',
         'avg_low': 'F',
         'days_high_above': 'days'}
PRECISION = {'total_precip': 2,
             'gdd': 1,
             'sdd': 1,
             'avg_temp': 1,
             'avg_high': 1,
             'avg_low': 1,
             'days_high_above': 1}
MDICT = OrderedDict([
         ('all', 'No Month/Time Limit'),
         ('spring', 'Spring (MAM)'),
         ('fall', 'Fall (SON)'),
         ('winter', 'Winter (DJF)'),
         ('summer', 'Summer (JJA)'),
         ('gs', '1 May to 30 Sep'),
         ('jan', 'January'),
         ('feb', 'February'),
         ('mar', 'March'),
         ('apr', 'April'),
         ('may', 'May'),
         ('jun', 'June'),
         ('jul', 'July'),
         ('aug', 'August'),
         ('sep', 'September'),
         ('oct', 'October'),
         ('nov', 'November'),
         ('dec', 'December')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This map produces an analysis of change in
    some climatological value between two periods of your choosing."""
    d['arguments'] = [
        dict(type='select', name='month', default='all',
             options=MDICT, label='Show Monthly or Annual Averages'),
        dict(type='select', name='sector', default='state',
             options=PDICT, label='Select Map Region'),
        dict(type='clstate', name='state', default='IA',
             label='Select State to Plot (when appropriate)'),
        dict(type='select', name='opt', options=PDICT2, default='both',
             label='Map Plot/Contour View Option'),
        dict(type='select', name='var', options=PDICT3, default='total_precip',
             label='Which Variable to Plot'),
        dict(type='text', name='threshold', default=-99,
             label='Enter threshold (where appropriate)'),
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
    varname = fdict.get('var', 'total_precip')
    sector = fdict.get('sector', 'state')
    threshold = float(fdict.get('threshold', -99))
    opt = fdict.get('opt', 'both')
    month = fdict.get('month', 'all')
    p1syear = int(fdict.get('p1syear', 1951))
    p1eyear = int(fdict.get('p1eyear', 1980))
    p2syear = int(fdict.get('p2syear', 1981))
    p2eyear = int(fdict.get('p2eyear', 2010))

    if month == 'all':
        months = range(1, 13)
    elif month == 'fall':
        months = [9, 10, 11]
    elif month == 'winter':
        months = [12, 1, 2]
    elif month == 'spring':
        months = [3, 4, 5]
    elif month == 'summer':
        months = [6, 7, 8]
    elif month == 'gs':
        months = [5, 6, 7, 8, 9]
    else:
        ts = datetime.datetime.strptime("2000-"+month+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month]

    table = "alldata"
    if sector == 'state':
        # optimization
        table = "alldata_%s" % (state,)

    df = read_sql("""
    WITH period1 as (
        SELECT station, year, sum(precip) as total_precip,
        avg((high+low) / 2.) as avg_temp, avg(high) as avg_high,
        avg(low) as avg_low,
        sum(gddxx(50, 86, high, low)) as sum_gdd,
        sum(case when high > 86 then high - 86 else 0 end) as sum_sdd,
        sum(case when high >= %s then 1 else 0 end) as days_high_above
        from """ + table + """ WHERE year >= %s and year < %s
        and month in %s GROUP by station, year),
    period2 as (
        SELECT station, year, sum(precip) as total_precip,
        avg((high+low) / 2.) as avg_temp, avg(high) as avg_high,
        avg(low) as avg_low,
        sum(gddxx(50, 86, high, low)) as sum_gdd,
        sum(case when high > 86 then high - 86 else 0 end) as sum_sdd,
        sum(case when high >= %s then 1 else 0 end) as days_high_above
        from """ + table + """ WHERE year >= %s and year < %s
        and month in %s GROUP by station, year),
    p1agg as (
        SELECT station, avg(total_precip) as precip,
        avg(avg_temp) as avg_temp, avg(avg_high) as avg_high,
        avg(avg_low) as avg_low, avg(sum_sdd) as sdd,
        avg(sum_gdd) as gdd,
        avg(days_high_above) as avg_days_high_above
        from period1 GROUP by station),
    p2agg as (
        SELECT station, avg(total_precip) as precip,
        avg(avg_temp) as avg_temp, avg(avg_high) as avg_high,
        avg(avg_low) as avg_low, avg(sum_sdd) as sdd,
        avg(sum_gdd) as gdd,
        avg(days_high_above) as avg_days_high_above
        from period2 GROUP by station),
    agg as (
        SELECT p2.station, p2.precip as p2_precip, p1.precip as p1_precip,
        p2.gdd as p2_gdd, p1.gdd as p1_gdd,
        p2.sdd as p2_sdd, p1.sdd as p1_sdd,
        p2.avg_temp as p2_avg_temp, p1.avg_temp as p1_avg_temp,
        p1.avg_high as p1_avg_high, p2.avg_high as p2_avg_high,
        p1.avg_low as p1_avg_low, p2.avg_low as p2_avg_low,
        p1.avg_days_high_above as p1_avg_days_high_above,
        p2.avg_days_high_above as p2_avg_days_high_above
        from p1agg p1 JOIN p2agg p2 on
        (p1.station = p2.station))

    SELECT station, ST_X(geom) as lon, ST_Y(geom) as lat,
    d.* from agg d JOIN stations t ON (d.station = t.id)
    WHERE t.network in ('IACLIMATE', 'NDCLIMATE', 'SDCLIMATE', 'NECLIMATE',
    'KSCLIMATE', 'MOCLIMATE', 'ILCLIMATE', 'WICLIMATE', 'MNCLIMATE',
    'MICLIMATE', 'INCLIMATE', 'OHCLIMATE', 'KYCLIMATE')
    and substr(station, 3, 1) != 'C' and substr(station, 3, 4) != '0000'
    """, pgconn, params=[threshold, p1syear, p1eyear, tuple(months),
                         threshold, p2syear, p2eyear, tuple(months)],
                  index_col=None)
    df['total_precip'] = df['p2_precip'] - df['p1_precip']
    df['avg_temp'] = df['p2_avg_temp'] - df['p1_avg_temp']
    df['avg_high'] = df['p2_avg_high'] - df['p1_avg_high']
    df['avg_low'] = df['p2_avg_low'] - df['p1_avg_low']
    df['gdd'] = df['p2_gdd'] - df['p1_gdd']
    df['sdd'] = df['p2_sdd'] - df['p1_sdd']
    df['days_high_above'] = (df['p2_avg_days_high_above'] -
                             df['p1_avg_days_high_above'])
    # Reindex so that most extreme values are first
    df = df.reindex(df[varname].abs().sort_values(ascending=False).index)

    title = "%s %s" % (MDICT[month], PDICT3[varname])
    title = title.replace("[Threshold]", '%.1f' % (threshold,))
    m = MapPlot(sector=sector, state=state, axisbg='white',
                title=('%.0f-%.0f minus %.0f-%.0f %s Difference'
                       ) % (p2syear, p2eyear, p1syear, p1eyear, title),
                subtitle=('based on IEM Archives'),
                titlefontsize=14)
    # Create 9 levels centered on zero
    abval = df[varname].abs().max()
    levels = centered_bins(abval)
    if opt in ['both', 'contour']:
        m.contourf(df['lon'].values, df['lat'].values,
                   df[varname].values, levels,
                   cmap=plt.get_cmap(('seismic_r' if varname == 'total_precip'
                                      else 'seismic')),
                   units=UNITS[varname])
    if sector == 'state':
        m.drawcounties()
    if opt in ['both', 'values']:
        m.plot_values(df['lon'].values, df['lat'].values,
                      df[varname].values,
                      fmt='%%.%if' % (PRECISION[varname],))

    return m.fig, df

if __name__ == '__main__':
    plotter(dict(over='annual'))
