"""map of climodat departures"""
import datetime
from collections import OrderedDict

import numpy as np
import psycopg2
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context

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
    ('midwest', 'Midwest US')])

PDICT2 = OrderedDict([
    ('avg_temp_depart', 'Average Temperature Departure'),
    ('min_low_temp', 'Minimum Low Temperature'),
    ('gdd_sum', 'Growing Degree Days (50/86) Total'),
    ('cgdd_sum', 'Growing Degree Days Climatology (50/86)'),
    ('gdd_depart', 'Growing Degree Days (50/86) Departure'),
    ('precip_depart', 'Precipitation Departure'),
    ])
PDICT4 = {'yes': 'Yes, overlay Drought Monitor',
          'no': 'No, do not overlay Drought Monitor'}
UNITS = {
    'precip_depart': 'inch',
    'min_low_temp': 'F',
    'gdd_depart': 'F',
    'gdd_sum': 'F',
    'cgdd_sum': 'F',
    'avg_temp_depart': 'F',
    }


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This application plots an analysis of station
    data for a period of your choice.  Spatially aggregated values like those
    for climate districts and statewide averages are not included.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc['arguments'] = [
        dict(type='select', name='sector', default='IA',
             label='Plot Sector:', options=PDICT),
        dict(type='select', name='var', default='precip_depart',
             label='Which Variable to Plot:', options=PDICT2),
        dict(type='date', name='date1',
             default=(today -
                      datetime.timedelta(days=30)).strftime("%Y/%m/%d"),
             label='Start Date:', min="1893/01/01"),
        dict(type='select', name='usdm', default='no',
             label='Overlay Drought Monitor', options=PDICT4),
        dict(type='date', name='date2',
             default=today.strftime("%Y/%m/%d"),
             label='End Date (inclusive):', min="1893/01/01"),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    import matplotlib.cm as cm

    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    sector = ctx['sector']
    date1 = ctx['date1']
    date2 = ctx['date2']
    varname = ctx['var']
    usdm = ctx['usdm']

    table = "alldata_%s" % (sector, ) if sector != 'midwest' else "alldata"
    df = read_sql("""
    WITH obs as (
        SELECT station, gddxx(50, 86, high, low) as gdd50,
        sday, high, low, precip from """ + table + """ WHERE
        day >= %s and day < %s and
        substr(station, 3, 1) != 'C' and substr(station, 3, 4) != '0000'),
    climo as (
        SELECT station, to_char(valid, 'mmdd') as sday, precip, high, low,
        gdd50 from climate51),
    combo as (
        SELECT o.station, o.precip - c.precip as precip_diff,
        o.high, o.low, o.gdd50, c.gdd50 as cgdd50,
        o.gdd50 - c.gdd50 as gdd50_diff,
        (o.high + o.low)/2. - (c.high + c.low)/2. as temp_diff
        from obs o JOIN climo c ON
        (o.station = c.station and o.sday = c.sday)),
    agg as (
        SELECT station, sum(precip_diff) as precip_depart,
        min(low) as min_low_temp, sum(gdd50_diff) as gdd_depart,
        avg(temp_diff) as avg_temp_depart, sum(gdd50) as gdd_sum,
        sum(cgdd50) as cgdd_sum
        from combo GROUP by station)

    SELECT d.station, d.precip_depart, d.min_low_temp, d.avg_temp_depart,
    d.gdd_depart, d.gdd_sum, d.cgdd_sum,
    ST_x(t.geom) as lon, ST_y(t.geom) as lat
    from agg d JOIN stations t on (d.station = t.id)
    WHERE t.network ~* 'CLIMATE'
    """, pgconn, params=(date1, date2), index_col='station')
    df = df.reindex(df[varname].abs().sort_values(ascending=False).index)

    sector2 = "state" if sector != 'midwest' else 'midwest'
    mp = MapPlot(sector=sector2, state=sector, axisbg='white',
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
    cmap = cm.get_cmap('RdYlBu' if varname == 'precip_depart' else 'RdYlBu_r')
    cmap.set_bad('white')
    mp.contourf(df['lon'].values, df['lat'].values,
                df[varname].values, clevels, clevlabels=clevlabels,
                cmap=cmap, units=UNITS.get(varname))
    mp.plot_values(df['lon'].values, df['lat'].values,
                   df[varname].values, fmt=fmt, labelbuffer=10)
    if sector == 'IA':
        mp.drawcounties()
    if usdm == 'yes':
        mp.draw_usdm(date2, filled=False, hatched=True)

    return mp.fig, df


if __name__ == '__main__':
    plotter(dict())
