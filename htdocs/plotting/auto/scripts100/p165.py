import numpy as np
from pyiem import util
import datetime
from pandas.io.sql import read_sql
import psycopg2
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
PDICT3 = {'contour': 'Contour + Plot Values',
          'values': 'Plot Values Only'}
PDICT2 = {'spring_below': 'Last Spring Date Below',
          'fall_below': 'First Fall Date Below'}
SQLOPT = {
    'spring_below': (" max(case when low < %s and month < 7 then "
                     " extract(doy from day) else -1 end) "),
    'fall_below': (" min(case when low < %s and month >= 7 then "
                   " extract(doy from day) else 400 end) ")}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This map presents the first fall date or last spring
    date with a temperature at/above or below some threshold.  The year is
    split on 1 July for the purposes of this plotting app.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    d['arguments'] = [
        dict(type='select', name='sector', default='IA',
             label='Select Sector:', options=PDICT),
        dict(type='select', name='var', default='spring_below',
             label='Select Plot Type:', options=PDICT2),
        dict(type='select', name='popt', default='contour',
             label='Plot Display Options:', options=PDICT3),
        dict(type='year', name='year',
             default=today.year,
             label='Start Year:', min=1893),
        dict(type='int', name='threshold',
             default=32,
             label='Temperature Threshold (F):'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    pgconn = psycopg2.connect(dbname='coop', host='iemdb', user='nobody')
    ctx = util.get_autoplot_context(fdict, get_description())
    sector = ctx['sector']
    varname = ctx['var']
    year = ctx['year']
    popt = ctx['popt']
    threshold = ctx['threshold']
    table = "alldata_%s" % (sector,)
    df = read_sql("""
    WITH data as (
        SELECT station, """ + SQLOPT[varname] + """ as doy
        from """ + table + """
        WHERE year = %s GROUP by station
    )
    select station, doy, st_x(geom) as lon, st_y(geom) as lat
    from data d JOIN stations t on (d.station = t.id) WHERE
    t.network = %s and substr(station, 3, 4) != '0000'
    and substr(station, 3, 1) != 'C' and doy not in (0, 400) ORDER by doy
    """, pgconn, params=(threshold, year, '%sCLIMATE' % (sector,)),
                  index_col='station')
    if len(df.index) == 0:
        return "No data found!"

    def f(val):
        ts = datetime.date(year, 1, 1) + datetime.timedelta(days=(val - 1))
        return ts.strftime("%-m/%-d")

    df['pdate'] = df['doy'].apply(f)

    m = MapPlot(sector='state', state=sector, axisbg='white', nocaption=True,
                title="%s %s %s$^\circ$F" % (year, PDICT2[varname], threshold),
                subtitle='based on NWS COOP and IEM Daily Estimates')
    levs = np.linspace(df['doy'].min() - 3, df['doy'].max() + 3, 7, dtype='i')
    levlables = map(f, levs)
    if popt == 'contour':
        m.contourf(df['lon'], df['lat'], df['doy'], levs, clevlabels=levlables)
    m.plot_values(df['lon'], df['lat'], df['pdate'], labelbuffer=5)
    m.drawcounties()

    return m.fig, df
