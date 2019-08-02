"""Streaks from CLI sites"""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict([('precip', 'Last Measurable Precipitation'),
                     ('low', 'Low Temperature'),
                     ('high', 'High Temperature')])
SECTORS = OrderedDict([
    ('conus', 'CONUS'),
    ('cornbelt', 'Corn Belt'),
    ('midwest', 'Mid West'),
    ('state', 'Select a State'),
    ('cwa', 'Select a NWS Weather Forecast Office')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 3600
    desc['description'] = """This plot presents the current streak of days with
    a high or low temperature above or at/below the daily average temperature.
    You can also plot the number of days since last measurable precipitation
    event (trace events are counted as dry).
    This plot is based off of NWS CLI sites."""
    desc['arguments'] = [
        dict(type='select', name='var', default='high',
             label='Which parameter:', options=PDICT),
        dict(type='date', name='sdate',
             default=datetime.date.today().strftime("%Y/%m/%d"),
             label='Start Date:', min="2010/01/01"),
        dict(type='select', name='sector', default='conus',
             options=SECTORS, label='Select Map Extent'),
        dict(type='networkselect', name='wfo', network='WFO',
             default='DMX', label='Select WFO: (used when plotting wfo)'),
        dict(type='state', name='state',
             default='IA', label='Select State: (used when plotting state)'),

    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('iem')
    ctx = get_autoplot_context(fdict, get_description())
    varname = ctx['var']
    sector = ctx['sector']
    state = ctx['state']
    wfo = ctx['wfo']

    today = ctx['sdate']
    yesterday = today - datetime.timedelta(days=1)
    d180 = today - datetime.timedelta(days=180)

    df = read_sql("""
     with obs as (
      select station, valid,
      (case when low > low_normal then 1 else 0 end) as low_hit,
      (case when high > high_normal then 1 else 0 end) as high_hit,
      (case when precip >= 0.01 then 1 else 0 end) as precip_hit
      from cli_data
      where high is not null
      and high_normal is not null and low is not null and
      low_normal is not null
      and valid > %s and valid <= %s),

      totals as (
      SELECT station,
      max(case when low_hit = 0 then valid else %s end) as last_low_below,
      max(case when low_hit = 1 then valid else %s end) as last_low_above,
      max(case when high_hit = 0 then valid else %s end) as last_high_below,
      max(case when high_hit = 1 then valid else %s end) as last_high_above,
      max(case when precip_hit = 0 then valid else %s end) as last_dry,
      max(case when precip_hit = 1 then valid else %s end) as last_wet,
      count(*) as count from obs GROUP by station)

      SELECT station, last_low_below, last_low_above, last_high_below,
      last_high_above, last_dry, last_wet
      from totals where count > 170
    """, pgconn, params=(d180, today, d180, d180, d180, d180, d180, d180),
                  index_col='station')
    if df.empty:
        raise NoDataFound("No Data Found.")

    lats = []
    lons = []
    vals = []
    colors = []
    labels = []
    df['precip_days'] = (df['last_dry'] - df['last_wet']).dt.days
    df['low_days'] = (df['last_low_above'] - df['last_low_below']).dt.days
    df['high_days'] = (df['last_high_above'] - df['last_high_below']).dt.days
    # reorder the frame so that the largest values come first
    df = df.reindex(df[varname+'_days'].abs(
        ).sort_values(ascending=False).index)

    for station, row in df.iterrows():
        if station not in ctx['_nt'].sts:
            continue
        lats.append(ctx['_nt'].sts[station]['lat'])
        lons.append(ctx['_nt'].sts[station]['lon'])
        if varname == 'precip':
            last_wet = row['last_wet']
            days = 0 if last_wet in [today, yesterday] else row['precip_days']
        else:
            days = row[varname + '_days']
        vals.append(days)
        colors.append('r' if days > 0 else 'b')
        labels.append(station[1:])

    title = ('Consecutive Days with %s Temp '
             'above(+)/below(-) Average') % (varname.capitalize(),)
    if varname == 'precip':
        title = 'Days Since Last Measurable Precipitation'
    mp = MapPlot(sector=sector,
                 state=state,
                 cwa=(wfo if len(wfo) == 3 else wfo[1:]),
                 axisbg='tan', statecolor='#EEEEEE',
                 title=title,
                 subtitle=('based on NWS CLI Sites, map approximately '
                           'valid for %s') % (today.strftime("%-d %b %Y"), ))
    mp.plot_values(lons, lats, vals, color=colors, labels=labels,
                   labeltextsize=(8 if sector != 'state' else 12),
                   textsize=(12 if sector != 'state' else 16),
                   labelbuffer=10)

    return mp.fig, df


if __name__ == '__main__':
    plotter(dict(var='precip'))
