import psycopg2
from pyiem.network import Table as NetworkTable
import datetime
from pandas.io.sql import read_sql
from collections import OrderedDict

PDICT = OrderedDict([('precip', 'Last Measurable Precipitation'),
                     ('low', 'Low Temperature'),
                     ('high', 'High Temperature')])
SECTORS = OrderedDict([('conus', 'CONUS'),
                       ('midwest', 'Mid West'),
                       ('state', 'Select a State'),
                       ('cwa', 'Select a NWS Weather Forecast Office')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 3600
    d['description'] = """This plot presents the current streak of days with
    a high or low temperature above or at/below the daily average temperature.
    You can also plot the number of days since last measurable precipitation
    event (trace events are counted as dry).
    This plot is based off of NWS CLI sites."""
    d['arguments'] = [
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
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')

    varname = fdict.get('var', 'high')
    sector = fdict.get('sector', 'conus')
    state = fdict.get('state', 'IA')
    wfo = fdict.get('wfo', 'DMX')
    if varname not in PDICT:
        return None

    nt = NetworkTable("NWSCLI")
    today = datetime.datetime.strptime(fdict.get('sdate', '2015-01-01'),
                                       '%Y-%m-%d')
    yesterday = today - datetime.timedelta(days=1)
    d180 = today - datetime.timedelta(days=180)

    dbcol = 'high' if varname in ['precip', ] else varname
    df = read_sql("""
     with obs as (
      select station, valid,
      (case when """ + dbcol + """ > """ + dbcol + """_normal
      then 1 else 0 end) as hit,
      (case when precip >= 0.01 then 1 else 0 end) as precip_hit
      from cli_data
      where """ + dbcol + """ is not null
      and """ + dbcol + """_normal is not null
      and valid > %s and valid <= %s),

      totals as (
      SELECT station,
      max(case when hit = 0 then valid else %s end) as last_below,
      max(case when hit = 1 then valid else %s end) as last_above,
      max(case when precip_hit = 0 then valid else %s end) as last_dry,
      max(case when precip_hit = 1 then valid else %s end) as last_wet,
      count(*) as count from obs GROUP by station)

      SELECT station, last_below, last_above, last_dry, last_wet
      from totals where count > 170
      ORDER by least(last_below, last_above) ASC
    """, pgconn, params=(d180, today, d180, d180, d180, d180))

    lats = []
    lons = []
    vals = []
    colors = []
    labels = []

    for _, row in df.iterrows():
        if row['station'] not in nt.sts:
            continue
        lats.append(nt.sts[row['station']]['lat'])
        lons.append(nt.sts[row['station']]['lon'])
        if varname == 'precip':
            last_wet = row['last_wet']
            last_dry = row['last_dry']
            days = (last_dry - last_wet).days
            if last_wet in [today, yesterday]:
                days = 0
        else:
            last_above = row['last_above']
            last_below = row['last_below']
            days = 0 - (last_below - last_above).days
            if last_above in [today, yesterday]:
                days = (last_above - last_below).days
        vals.append(days)
        colors.append('r' if days > 0 else 'b')
        labels.append(row[0])

    title = ('Consecutive Days with %s Temp '
             'above(+)/below(-) Average') % (varname.capitalize(),)
    if varname == 'precip':
        title = 'Days Since Last Measurable Precipitation'
    m = MapPlot(sector=sector,
                state=state,
                cwa=(wfo if len(wfo) == 3 else wfo[1:]),
                axisbg='tan', statecolor='#EEEEEE',
                title=title,
                subtitle=('based on NWS CLI Sites, map approximately '
                          'valid for %s') % (today.strftime("%-d %b %Y"), ))
    m.plot_values(lons, lats, vals, color=colors, labels=labels,
                  labeltextsize=(8 if sector != 'state' else 12),
                  textsize=(12 if sector != 'state' else 16),
                  labelbuffer=10)

    return m.fig, df
