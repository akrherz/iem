"""map of climodat departures"""
import datetime
from collections import OrderedDict

import numpy as np
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn

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
    ('max_high_temp', 'Maximum High Temperature'),
    ('avg_high_temp', 'Average High Temperature'),
    ('avg_temp_depart', 'Average Temperature Departure'),
    ('avg_temp', 'Average Temperature'),
    ('min_low_temp', 'Minimum Low Temperature'),
    ('avg_low_temp', 'Average Low Temperature'),
    ('gdd_sum', 'Growing Degree Days (50/86) Total'),
    ('cgdd_sum', 'Growing Degree Days Climatology (50/86)'),
    ('gdd_depart', 'Growing Degree Days (50/86) Departure'),
    ('precip_depart', 'Precipitation Departure'),
    ('precip_sum', 'Precipitation Total'),
    ])
PDICT4 = {'yes': 'Yes, overlay Drought Monitor',
          'no': 'No, do not overlay Drought Monitor'}
UNITS = {
    'precip_depart': 'inch',
    'min_low_temp': 'F',
    'avg_low_temp': 'F',
    'avg_high_temp': 'F',
    'gdd_depart': 'F',
    'gdd_sum': 'F',
    'cgdd_sum': 'F',
    'avg_temp_depart': 'F',
    'avg_temp': 'F',
    'precip_sum': 'inch',
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

    pgconn = get_dbconn('coop')
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
        sday, high, low, precip,
        (high + low)/2. as avg_temp
        from """ + table + """ WHERE
        day >= %s and day < %s and
        substr(station, 3, 1) != 'C' and substr(station, 3, 4) != '0000'),
    climo as (
        SELECT station, to_char(valid, 'mmdd') as sday, precip, high, low,
        gdd50 from climate51),
    combo as (
        SELECT o.station, o.precip - c.precip as precip_diff,
        o.precip as precip, c.precip as cprecip,
        o.avg_temp,
        o.high, o.low, o.gdd50, c.gdd50 as cgdd50,
        o.gdd50 - c.gdd50 as gdd50_diff,
        o.avg_temp - (c.high + c.low)/2. as temp_diff
        from obs o JOIN climo c ON
        (o.station = c.station and o.sday = c.sday)),
    agg as (
        SELECT station,
        avg(avg_temp) as avg_temp,
        sum(precip_diff) as precip_depart,
        sum(precip) as precip, sum(cprecip) as cprecip,
        avg(high) as avg_high_temp,
        avg(low) as avg_low_temp,
        max(high) as max_high_temp,
        min(low) as min_low_temp, sum(gdd50_diff) as gdd_depart,
        avg(temp_diff) as avg_temp_depart, sum(gdd50) as gdd_sum,
        sum(cgdd50) as cgdd_sum
        from combo GROUP by station)

    SELECT d.station, t.name,
    precip as precip_sum,
    avg_temp,
    cprecip as cprecip_sum,
    precip_depart,
    min_low_temp,
    avg_temp_depart,
    gdd_depart,
    gdd_sum,
    cgdd_sum,
    max_high_temp,
    avg_high_temp,
    avg_low_temp,
    ST_x(t.geom) as lon, ST_y(t.geom) as lat
    from agg d JOIN stations t on (d.station = t.id)
    WHERE t.network ~* 'CLIMATE'
    """, pgconn, params=(date1, date2), index_col='station')
    df = df.reindex(df[varname].abs().sort_values(ascending=False).index)

    sector2 = "state" if sector != 'midwest' else 'midwest'
    datefmt = "%d %b %Y" if varname != 'cgdd_sum' else '%d %b'
    subtitle = ''
    if varname.find('depart') > -1:
        subtitle = ('%s is compared with 1951-%s Climatology'
                    ' to compute departures'
                    ) % (date1.year, datetime.date.today().year - 1)
    elif varname.startswith('c'):
        subtitle = ("Climatology is based on data from 1951-%s"
                    ) % (datetime.date.today().year - 1, )
    mp = MapPlot(sector=sector2, state=sector, axisbg='white',
                 title=('%s - %s %s [%s]'
                        ) % (date1.strftime(datefmt),
                             date2.strftime(datefmt), PDICT2.get(varname),
                             UNITS.get(varname)),
                 subtitle=subtitle)
    fmt = '%.2f'
    if varname in ['precip_depart', 'avg_temp_depart']:
        rng = df[varname].abs().describe(percentiles=[0.95])['95%']
        clevels = np.linspace(0 - rng, rng, 7)
        cmap = cm.get_cmap('RdYlBu'
                           if varname == 'precip_depart' else 'RdYlBu_r')
    elif varname in ['precip_sum']:
        rng = df[varname].abs().describe(percentiles=[0.95])['95%']
        clevels = np.linspace(0, rng, 7)
        cmap = cm.get_cmap('plasma_r')
        cmap.set_under('white')
        cmap.set_over('black')
    else:
        minv = df[varname].min() - 5
        maxv = df[varname].max() + 5
        clevels = np.linspace(minv, maxv, 6, dtype='i')
        fmt = '%.0f'
        cmap = cm.get_cmap('RdYlBu_r')
    clevlabels = [fmt % x for x in clevels]
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
