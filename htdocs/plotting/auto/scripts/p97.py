"""map of climodat departures"""
import datetime
from collections import OrderedDict

import numpy as np
from pandas.io.sql import read_sql
import matplotlib.cm as cm
from pyiem.plot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT2 = OrderedDict([
    ('max_high_temp', 'Maximum High Temperature'),
    ('avg_high_temp', 'Average High Temperature'),
    ('avg_temp_depart', 'Average Temperature Departure'),
    ('avg_temp', 'Average Temperature'),
    ('min_low_temp', 'Minimum Low Temperature'),
    ('avg_low_temp', 'Average Low Temperature'),
    ('gdd_sum', 'Growing Degree Days ($base/86) Total'),
    ('cgdd_sum', 'Growing Degree Days Climatology ($base/86)'),
    ('gdd_depart', 'Growing Degree Days ($base/86) Departure'),
    ('gdd_percent', 'GDD ($base/86) Percent of Average'),
    ('cdd65_sum', 'Cooling Degree Days (base 65)'),
    ('cdd65_depart', 'Cooling Degree Days Departure (base 65)'),
    ('hdd65_sum', 'Heating Degree Days (base 65)'),
    ('hdd65_depart', 'Heating Degree Days Departure (base 65)'),
    ('precip_depart', 'Precipitation Departure'),
    ('precip_sum', 'Precipitation Total'),
    ])
BASES = OrderedDict([('32', 32), ('41', 41), ('46', 46), ('48', 48),
                     ('50', 50), ('51', 51), ('52', 52)])
PDICT4 = {'yes': 'Yes, overlay Drought Monitor',
          'no': 'No, do not overlay Drought Monitor'}
UNITS = {
    'precip_depart': 'inch',
    'min_low_temp': 'F',
    'avg_low_temp': 'F',
    'avg_high_temp': 'F',
    'gdd_depart': 'F',
    'gdd_percet': '%',
    'gdd_sum': 'F',
    'cdd_sum': 'F',
    'hdd_sum': 'F',
    'cdd_depart': 'F',
    'hdd_depart': 'F',
    'cgdd_sum': 'F',
    'avg_temp_depart': 'F',
    'avg_temp': 'F',
    'precip_sum': 'inch',
    }
PDICT3 = {'contour': 'Contour the data',
          'text': 'Plot just values without contours'}
PDICT5 = {
    'yes': "Label Station Values",
    'no': "Do Not Label Station Values"
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This application plots an analysis of station
    data for a period of your choice.  Spatially aggregated values like those
    for climate districts and statewide averages are not included.  For this
    application, climatology is based on averaged observations between 1951
    till the present day.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc['arguments'] = [
        dict(type='csector', name='sector', default='IA',
             label='Plot Sector:'),
        dict(type='select', name='var', default='precip_depart',
             label='Which Variable to Plot:', options=PDICT2),
        dict(type='select', options=BASES, default=50, name='gddbase',
             label='Available Growing Degree Day bases (F)'),
        dict(type='date', name='date1',
             default=(today -
                      datetime.timedelta(days=30)).strftime("%Y/%m/%d"),
             label='Start Date:', min="1893/01/01"),
        dict(type='select', name='usdm', default='no',
             label='Overlay Drought Monitor', options=PDICT4),
        dict(type='date', name='date2',
             default=today.strftime("%Y/%m/%d"),
             label='End Date (inclusive):', min="1893/01/01"),
        dict(type='select', name='p', default='contour',
             label='Data Presentation Options', options=PDICT3),
        dict(type='cmap', name='cmap', default='RdYlBu', label='Color Ramp:'),
        dict(
            type='select', options=PDICT5, default='yes', name='c',
            label='Label Values?',
        )
    ]
    return desc


def plotter(fdict):
    """ Go """

    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    sector = ctx['sector']
    date1 = ctx['date1']
    date2 = ctx['date2']
    varname = ctx['var']

    table = "alldata_%s" % (sector, ) if len(sector) == 2 else "alldata"
    state_limiter = ""
    if sector == 'iailin':
        state_limiter = (
            " and network in ('IACLIMATE', 'ILCLIMATE', 'INCLIMATE') "
        )
    df = read_sql("""
    WITH obs as (
        SELECT station, gddxx(%s, 86, high, low) as gdd,
        cdd(high, low, 65) as cdd65, hdd(high, low, 65) as hdd65,
        sday, high, low, precip,
        (high + low)/2. as avg_temp
        from """ + table + """ WHERE
        day >= %s and day < %s and
        substr(station, 3, 1) != 'C' and substr(station, 3, 4) != '0000'),
    climo as (
        SELECT station, to_char(valid, 'mmdd') as sday, precip, high, low,
        gdd""" + str(ctx['gddbase']) + """ as gdd, cdd65, hdd65
        from climate51),
    combo as (
        SELECT o.station, o.precip - c.precip as precip_diff,
        o.precip as precip, c.precip as cprecip,
        o.avg_temp, o.cdd65, o.hdd65,
        o.high, o.low, o.gdd, c.gdd as cgdd,
        o.gdd - c.gdd as gdd_diff,
        o.cdd65 - c.cdd65 as cdd_diff,
        o.hdd65 - c.hdd65 as hdd_diff,
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
        min(low) as min_low_temp, sum(gdd_diff) as gdd_depart,
        sum(gdd) / greatest(1, sum(cgdd)) * 100. as gdd_percent,
        avg(temp_diff) as avg_temp_depart, sum(gdd) as gdd_sum,
        sum(cgdd) as cgdd_sum,
        sum(cdd65) as cdd_sum,
        sum(hdd65) as hdd_sum,
        sum(cdd_diff) as cdd_depart,
        sum(hdd_diff) as hdd_depart
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
    gdd_percent,
    cgdd_sum,
    max_high_temp,
    avg_high_temp,
    avg_low_temp,
    cdd_sum, hdd_sum, cdd_depart, hdd_depart,
    ST_x(t.geom) as lon, ST_y(t.geom) as lat
    from agg d JOIN stations t on (d.station = t.id)
    WHERE t.network ~* 'CLIMATE' """ + state_limiter + """
    """, pgconn, params=(ctx['gddbase'], date1, date2), index_col='station')
    if df.empty:
        raise NoDataFound("No Data Found.")
    df = df.reindex(df[varname].abs().sort_values(ascending=False).index)

    datefmt = "%d %b %Y" if varname != 'cgdd_sum' else '%d %b'
    subtitle = ''
    if varname.find('depart') > -1:
        subtitle = ('%s is compared with 1951-%s Climatology'
                    ' to compute departures'
                    ) % (date1.year, datetime.date.today().year - 1)
    elif varname.startswith('c'):
        subtitle = ("Climatology is based on data from 1951-%s"
                    ) % (datetime.date.today().year - 1, )
    mp = MapPlot(
        sector="state" if len(sector) == 2 else sector,
        state=sector, axisbg='white',
        title='%s - %s %s [%s]' % (
            date1.strftime(datefmt), date2.strftime(datefmt),
            PDICT2.get(varname).replace("$base", str(ctx['gddbase'])),
            UNITS.get(varname)),
        subtitle=subtitle)
    fmt = '%.2f'
    cmap = cm.get_cmap(ctx['cmap'])
    if varname in ['precip_depart', 'avg_temp_depart', 'gdd_depart']:
        rng = df[varname].abs().describe(percentiles=[0.95])['95%']
        clevels = np.linspace(
            0 - rng, rng, 7,
            dtype='i' if varname == 'gdd_depart' else 'f')
        if varname == 'gdd_depart':
            fmt = '%.0f'
    elif varname in ['precip_sum']:
        rng = df[varname].abs().describe(percentiles=[0.95])['95%']
        clevels = np.linspace(0, rng, 7)
        cmap.set_under('white')
        cmap.set_over('black')
    elif varname.endswith("_percent"):
        clevels = np.array([10, 25, 50, 75, 100, 125, 150, 175, 200])
        fmt = '%.0f'
    else:
        minv = df[varname].min() - 5
        maxv = df[varname].max() + 5
        clevels = np.linspace(minv, maxv, 6, dtype='i')
        fmt = '%.0f'
    clevlabels = [fmt % x for x in clevels]
    cmap.set_bad('white')
    if ctx['p'] == 'contour':
        mp.contourf(df['lon'].values, df['lat'].values,
                    df[varname].values, clevels, clevlabels=clevlabels,
                    cmap=cmap, units=UNITS.get(varname))
    if ctx['c'] == 'yes':
        mp.plot_values(
            df['lon'].values, df['lat'].values,
            df[varname].values, fmt=fmt, labelbuffer=5)
    if len(sector) == 2 or sector == 'iailin':
        mp.drawcounties()
    if ctx['usdm'] == 'yes':
        mp.draw_usdm(date2, filled=False, hatched=True)

    return mp.fig, df


if __name__ == '__main__':
    plotter(dict())
