import numpy as np
import datetime
import psycopg2
import pandas as pd
from collections import OrderedDict

PDICT = OrderedDict({'IA': 'Iowa',
                     'IL': 'Illinois',
                     'KS': 'Kansas',
                     'KY': 'Kentucky',
                     'MI': 'Michigan',
                     'MN': 'Minnesota',
                     'MO': 'Missouri',
                     'NE': 'Nebraska',
                     'ND': 'North Dakota',
                     'OH': 'Ohio',
                     'SD': 'South Dakota',
                     'WI': 'Wisconsin',
                     'midwest': 'Mid West US'}
                    )


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This application plots an analysis of station
    precipitation departures for a period of your choice.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    d['arguments'] = [
        dict(type='select', name='sector', default='IA',
             label='Plot Sector:', options=PDICT),
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
    cursor = pgconn.cursor()

    sector = fdict.get('sector', 'IA')
    date1 = datetime.datetime.strptime(fdict.get('date1', '2015-01-01'),
                                       '%Y-%m-%d')
    date2 = datetime.datetime.strptime(fdict.get('date2', '2015-02-01'),
                                       '%Y-%m-%d')

    table = "alldata_%s" % (sector, ) if sector != 'midwest' else "alldata"
    cursor.execute("""
    WITH obs as (
        SELECT station, sday, day, precip from """ + table + """ WHERE
        day >= %s and day < %s and precip >= 0 and
        substr(station, 3, 1) != 'C' and substr(station, 3, 4) != '0000'),
    climo as (
        SELECT station, to_char(valid, 'mmdd') as sday, precip from
        climate51),
    combo as (
        SELECT o.station, o.precip - c.precip as d from obs o JOIN climo c ON
        (o.station = c.station and o.sday = c.sday)),
    deltas as (
        SELECT station, sum(d) from combo GROUP by station)

    SELECT d.station, d.sum, ST_x(t.geom), ST_y(t.geom) from deltas d
    JOIN stations t on (d.station = t.id) WHERE t.network ~* 'CLIMATE'
    """, (date1, date2))

    rows = []
    for row in cursor:
        rows.append(dict(station=row[0], delta=row[1], lon=row[2],
                         lat=row[3]))
    df = pd.DataFrame(rows)
    lons = np.array(df['lon'])
    vals = np.array(df['delta'])
    lats = np.array(df['lat'])
    sector2 = "state" if sector != 'midwest' else 'midwest'
    m = MapPlot(sector=sector2, state=sector, axisbg='white',
                title=('%s - %s Precipitation Departure [inch]'
                       ) % (date1.strftime("%d %b %Y"),
                            date2.strftime("%d %b %Y")),
                subtitle='%s vs 1950-2014 Climatology' % (date1.year,))
    rng = int(max([0 - np.min(vals), np.max(vals)]))
    cmap = cm.get_cmap('RdYlBu')
    cmap.set_bad('white')
    m.contourf(lons, lats, vals, np.linspace(0 - rng - 0.5, rng + 0.6, 10,
                                             dtype='i'),
               cmap=cmap, units='inch')
    m.plot_values(lons, lats, vals, fmt='%.2f')
    if sector == 'iowa':
        m.drawcounties()

    return m.fig, df
