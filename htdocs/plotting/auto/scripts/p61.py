
import psycopg2.extras
from pyiem.network import Table as NetworkTable
import datetime

PDICT = {'low': 'Low Temperature',
         'high': 'High Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 3600
    d['description'] = """This plot presents the current streak of days with
    a high or low temperature above or at/below the daily average temperature.
    This plot is based off of NWS CLI sites."""
    d['arguments'] = [
        dict(type='select', name='var', default='high',
             label='Which parameter:', options=PDICT),
        dict(type='date', name='sdate',
             default=datetime.date.today().strftime("%Y/%m/%d"),
             label='Start Date:', min="2010/01/01")
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    varname = fdict.get('var', 'high')
    if varname not in PDICT:
        return None

    nt = NetworkTable("NWSCLI")
    today = datetime.datetime.strptime(fdict.get('sdate', '2015-01-01'),
                                       '%Y-%m-%d')
    yesterday = today - datetime.timedelta(days=1)
    d180 = today - datetime.timedelta(days=180)

    cursor.execute("""
     with obs as (
      select station, valid,
      (case when """ + varname + """ > """ + varname + """_normal
      then 1 else 0 end) as hit from cli_data
      where """ + varname + """ is not null
      and """ + varname + """_normal is not null
      and valid > %s and valid <= %s),

      totals as (
      SELECT station,
      max(case when hit = 0 then valid else %s end) as last_below,
      max(case when hit = 1 then valid else %s end) as last_above,
      count(*) as count from obs GROUP by station)

      SELECT station, last_below, last_above from totals where count > 170
      ORDER by least(last_below, last_above) ASC
    """, (d180, today, d180, d180))

    lats = []
    lons = []
    vals = []
    colors = []
    labels = []

    for row in cursor:
        if row[0] not in nt.sts:
            continue
        lats.append(nt.sts[row[0]]['lat'])
        lons.append(nt.sts[row[0]]['lon'])
        last_above = row[2]
        last_below = row[1]
        days = 0 - (last_below - last_above).days
        if last_above in [today, yesterday]:
            days = (last_above - last_below).days
        vals.append(days)
        colors.append('r' if days > 0 else 'b')
        labels.append(row[0])

    m = MapPlot(sector='conus', axisbg='tan', statecolor='#EEEEEE',
                title=('Consecutive Days with %s Temp '
                       'above(+)/below(-) Average') % (varname.capitalize(),),
                subtitle=('based on NWS CLI Sites, map approximately '
                          'valid for %s') % (today.strftime("%-d %b %Y"), ))
    m.plot_values(lons, lats, vals, color=colors, labels=labels,
                  labeltextsize=8, textsize=12)

    return m.fig
