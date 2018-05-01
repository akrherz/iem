"""Climate District ranks"""
import datetime
import calendar
from collections import OrderedDict

import matplotlib.cm as cm
import numpy as np
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = OrderedDict((
    ('arridity', 'Arridity Index'),
    ('avgt', 'Average Temperature'),
    ('high', 'Average High Temperature'),
    ('low', 'Average Low Temperature'),
    ('precip', 'Total Precipitation'),
    ))

MDICT = OrderedDict([
         ('spring', 'Spring (MAM)'),
         ('fall', 'Fall (SON)'),
         ('winter', 'Winter (DJF)'),
         ('summer', 'Summer (JJA)'),
         ('1', 'January'),
         ('2', 'February'),
         ('3', 'March'),
         ('4', 'April'),
         ('5', 'May'),
         ('6', 'June'),
         ('7', 'July'),
         ('8', 'August'),
         ('9', 'September'),
         ('10', 'October'),
         ('11', 'November'),
         ('12', 'December')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This map presents IEM computed precipitation
    ranks for a month and year of your choice.  The map unit is climate
    districts for which the IEM generates spatially weighted daily averages
    for.  For seasonal totals, the year presented is the calendar year of
    the last month in the three month period."""
    today = datetime.date.today() - datetime.timedelta(days=28)
    desc['arguments'] = [
        dict(type='select', name='var', default='precip',
             label='Select Variable', options=PDICT),
        dict(type='year', name='year', default=today.year,
             label='Select Year:',
             min=1893),
        dict(type='select', name='month', default=today.month,
             label='Month Limiter', options=MDICT),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())

    year = ctx['year']
    month = ctx['month']
    varname = ctx['var']
    offset = "0 days"
    if month == 'fall':
        months = [9, 10, 11]
        label = "Fall (SON)"
    elif month == 'winter':
        months = [12, 1, 2]
        offset = "32 days"
        label = "Winter (DJF)"
    elif month == 'spring':
        months = [3, 4, 5]
        label = "Spring (MAM)"
    elif month == 'summer':
        months = [6, 7, 8]
        label = "Summer (JJA)"
    else:
        months = [int(month), ]
        label = calendar.month_name[int(month)]

    lastyear = datetime.date.today().year
    years = lastyear - 1893 + 1

    df = read_sql("""
    with monthly as (
        SELECT extract(year from day + '""" + offset + """'::interval) as myyear,
        station, sum(precip) as p,
        avg((high+low)/2.) as avgt,
        avg(low) as avglo,
        avg(high) as avghi
        from alldata
        WHERE substr(station,3,1) = 'C' and month in %s
        GROUP by myyear, station),
    ranks as (
        SELECT station, myyear as year,
        avg(p) OVER (PARTITION by station) as avg_precip,
        stddev(p) OVER (PARTITION by station) as std_precip,
        p as precip,
        avg(avghi) OVER (PARTITION by station) as avg_high,
        stddev(avghi) OVER (PARTITION by station) as std_high,
        avghi as high,
        avg(avglo) OVER (PARTITION by station) as avg_low,
        stddev(avglo) OVER (PARTITION by station) as std_low,
        avglo as low,
        rank() OVER (PARTITION by station ORDER by p DESC) as precip_rank,
        rank() OVER (PARTITION by station ORDER by avghi DESC) as high_rank,
        rank() OVER (PARTITION by station ORDER by avglo DESC) as low_rank,
        rank() OVER (PARTITION by station ORDER by avgt DESC) as avgt_rank
        from monthly)

    SELECT station, precip_rank, avgt_rank, high_rank, low_rank,
    ((high - avg_high) / std_high) - ((precip - avg_precip) / std_precip)
    as arridity from ranks
    where year = %s and
    substr(station, 1, 2) in ('ND', 'SD', 'NE', 'KS', 'MO', 'IA', 'MN', 'WI',
    'IL', 'IN', 'KY', 'OH', 'MI')
    """, pgconn, params=(tuple(months), year),
                  index_col='station')

    subtitle = ('Based on IEM Estimates, '
                '1 is %s out of %s total years (1893-%s)'
                ) % ('wettest' if varname == 'precip' else 'hottest',
                     years, lastyear)
    if varname == 'arridity':
        subtitle = "Std Average High Temp Departure minus Std Precip Departure"
    mp = MapPlot(sector='midwest', continentalcolor='white',
                 title='%s %s %s %sby Climate District' % (
                         year, label, PDICT[varname],
                         'Ranks ' if varname != 'arridity' else ''),
                 subtitle=subtitle)
    cmap = cm.get_cmap("BrBG_r" if varname in ['precip', 'arridity']
                       else 'BrBG')
    cmap.set_under('white')
    cmap.set_over('black')
    bins = [1, 5, 10, 25, 50, 75, 100, years-10, years-5, years]
    pvar = varname+'_rank'
    fmt = '%.0f'
    if varname == 'arridity':
        bins = np.arange(-4, 4.1, 1)
        pvar = varname
        fmt = '%.1f'
    mp.fill_climdiv(df[pvar], ilabel=True, plotmissing=False, lblformat=fmt,
                    bins=bins,
                    cmap=cmap)

    return mp.fig, df


if __name__ == '__main__':
    plotter(dict())
