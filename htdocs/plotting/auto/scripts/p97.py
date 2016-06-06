import numpy as np
import datetime
import psycopg2
from pandas.io.sql import read_sql
from collections import OrderedDict

PDICT = OrderedDict([
    ('IA', 'Iowa'),
    ('IL', 'Illinois'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MO', 'Missouri'),
    ('NE', 'Nebraska'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('SD', 'South Dakota'),
    ('WI', 'Wisconsin'),
    ('midwest', 'Mid West US')])

PDICT2 = OrderedDict([
    ('avg_temp_depart', 'Average Temperature Departure'),
    ('min_low_temp', 'Minimum Low Temperature'),
    ('precip_depart', 'Precipitation Departure'),
    ])

UNITS = {
    'precip_depart': 'inch',
    'min_low_temp': 'F',
    'avg_temp_depart': 'F',
    }


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This application plots an analysis of station
    data for a period of your choice.  Spatially aggregated values like those
    for climate districts and statewide averages are not included.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    d['arguments'] = [
        dict(type='select', name='sector', default='IA',
             label='Plot Sector:', options=PDICT),
        dict(type='select', name='var', default='precip_depart',
             label='Which Variable to Plot:', options=PDICT2),
        dict(type='date', name='date1',
             default=(today -
                      datetime.timedelta(days=30)).strftime("%Y/%m/%d"),
             label='Start Date:', min="1893/01/01"),
        dict(type='date', name='date2',
             default=today.strftime("%Y/%m/%d"),
             label='End Date (inclusive):', min="1893/01/01"),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    import matplotlib.cm as cm

    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    sector = fdict.get('sector', 'IA')
    date1 = datetime.datetime.strptime(fdict.get('date1', '2015-01-01'),
                                       '%Y-%m-%d')
    date2 = datetime.datetime.strptime(fdict.get('date2', '2015-02-01'),
                                       '%Y-%m-%d')
    varname = fdict.get('var', 'precip_depart')

    table = "alldata_%s" % (sector, ) if sector != 'midwest' else "alldata"
    df = read_sql("""
    WITH obs as (
        SELECT station, sday, high, low, precip from """ + table + """ WHERE
        day >= %s and day < %s and
        substr(station, 3, 1) != 'C' and substr(station, 3, 4) != '0000'),
    climo as (
        SELECT station, to_char(valid, 'mmdd') as sday, precip, high, low from
        climate51),
    combo as (
        SELECT o.station, o.precip - c.precip as precip_diff,
        o.high, o.low,
        (o.high + o.low)/2. - (c.high + c.low)/2. as temp_diff
        from obs o JOIN climo c ON
        (o.station = c.station and o.sday = c.sday)),
    agg as (
        SELECT station, sum(precip_diff) as precip_depart,
        min(low) as min_low_temp,
        avg(temp_diff) as avg_temp_depart from combo GROUP by station)

    SELECT d.station, d.precip_depart, d.min_low_temp, d.avg_temp_depart,
    ST_x(t.geom) as lon, ST_y(t.geom) as lat from agg d
    JOIN stations t on (d.station = t.id) WHERE t.network ~* 'CLIMATE'
    """, pgconn, params=(date1, date2), index_col='station')

    sector2 = "state" if sector != 'midwest' else 'midwest'
    m = MapPlot(sector=sector2, state=sector, axisbg='white',
                title=('%s - %s %s [%s]'
                       ) % (date1.strftime("%d %b %Y"),
                            date2.strftime("%d %b %Y"), PDICT2.get(varname),
                            UNITS.get(varname)),
                subtitle=('%s is compared with 1951-%s Climatology'
                          ' to compute departures'
                          ) % (date1.year, datetime.date.today().year - 1))
    if varname in ['precip_depart', 'avg_temp_depart']:
        rng = df[varname].abs().describe(percentiles=[0.95])['95%']
        clevels = np.linspace(0 - rng, rng, 7)
        fmt = '%.2f'
    else:
        minv = df[varname].min() - 5
        maxv = df[varname].max() + 5
        clevels = np.linspace(minv, maxv, 6, dtype='i')
        fmt = '%.0f'
    clevlabels = [fmt % x for x in clevels]
    cmap = cm.get_cmap('RdYlBu')
    cmap.set_bad('white')
    m.contourf(df['lon'].values, df['lat'].values,
               df[varname].values, clevels, clevlabels=clevlabels,
               cmap=cmap, units=UNITS.get(varname))
    m.plot_values(df['lon'].values, df['lat'].values,
                  df[varname].values, fmt=fmt, labelbuffer=15)
    if sector == 'IA':
        m.drawcounties()

    return m.fig, df
