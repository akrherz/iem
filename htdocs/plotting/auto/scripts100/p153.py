"""Highest hourly values"""
from collections import OrderedDict
import datetime

from pandas.io.sql import read_sql
from matplotlib.font_manager import FontProperties
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.network import Table as NetworkTable

PDICT = OrderedDict([
        ('max_dwpf', 'Highest Dew Point Temperature'),
        ('min_dwpf', 'Lowest Dew Point Temperature'),
        ('max_tmpf', 'Highest Air Temperature'),
        ('min_tmpf', 'Lowest Air Temperature'),
        ('max_feel', 'Highest Feels Like Temperature'),
        ('min_feel', 'Lowest Feels Like Temperature'),
        ('max_mslp', 'Maximum Sea Level Pressure'),
        ('min_mslp', 'Minimum Sea Level Pressure'),
        ('max_alti', 'Maximum Pressure Altimeter'),
        ('min_alti', 'Minimum Pressure Altimeter'),
        ])
UNITS = {'max_dwpf': 'F',
         'max_tmpf': 'F',
         'min_dwpf': 'F',
         'min_tmpf': 'F',
         'min_feel': 'F',
         'max_feel': 'F',
         'max_mslp': 'mb',
         'min_mslp': 'mb',
         'max_alti': 'in',
         'min_alti': 'in',
         }
MDICT = OrderedDict([
         ('all', 'No Month Limit'),
         ('spring', 'Spring (MAM)'),
         ('fall', 'Fall (SON)'),
         ('winter', 'Winter (DJF)'),
         ('summer', 'Summer (JJA)'),
         ('gs', '1 May to 30 Sep'),
         ('jan', 'January'),
         ('feb', 'February'),
         ('mar', 'March'),
         ('apr', 'April'),
         ('may', 'May'),
         ('jun', 'June'),
         ('jul', 'July'),
         ('aug', 'August'),
         ('sep', 'September'),
         ('oct', 'October'),
         ('nov', 'November'),
         ('dec', 'December')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This table presents the extreme hourly value of
    some variable of your choice based on available observations maintained
    by the IEM.  Sadly, this app will likely point out some bad data points
    as such points tend to be obvious at extremes.  If you contact us to
    point out troubles, we'll certainly attempt to fix the archive to
    remove the bad data points.  Observations are arbitrarly bumped 10
    minutes into the future to place the near to top of the hour obs on
    that hour.  For example, a 9:53 AM observation becomes the ob for 10 AM.
    """
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             network='IA_ASOS', label='Select Station:'),
        dict(type='select', name='month', default='all',
             options=MDICT, label='Select Month/Season/All'),
        dict(type='select', name='var', options=PDICT, default='max_dwpf',
             label='Which Variable to Plot'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    font0 = FontProperties()
    font0.set_family('monospace')
    font0.set_size(16)
    font1 = FontProperties()
    font1.set_size(16)

    pgconn = get_dbconn('asos')
    ctx = get_autoplot_context(fdict, get_description())
    varname = ctx['var']
    varname2 = varname.split("_")[1]
    if varname2 in ['dwpf', 'tmpf', 'feel']:
        varname2 = "i" + varname2
    month = ctx['month']
    network = ctx['network']
    station = ctx['zstation']
    nt = NetworkTable(network)

    if month == 'all':
        months = range(1, 13)
    elif month == 'fall':
        months = [9, 10, 11]
    elif month == 'winter':
        months = [12, 1, 2]
    elif month == 'spring':
        months = [3, 4, 5]
    elif month == 'summer':
        months = [6, 7, 8]
    elif month == 'gs':
        months = [5, 6, 7, 8, 9]
    else:
        ts = datetime.datetime.strptime("2000-"+month+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month]

    df = read_sql("""
    WITH obs as (
        SELECT (valid + '10 minutes'::interval) at time zone %s as ts,
        tmpf::int as itmpf, dwpf::int as idwpf,
        feel::int as ifeel, mslp, alti from alldata
        where station = %s and
        extract(month from valid at time zone %s) in %s),
    agg1 as (
        SELECT extract(hour from ts) as hr,
        max(idwpf) as max_dwpf,
        max(itmpf) as max_tmpf,
        min(idwpf) as min_dwpf,
        min(itmpf) as min_tmpf,
        min(ifeel) as min_feel,
        max(ifeel) as max_feel,
        max(alti) as max_alti,
        min(alti) as min_alti,
        max(mslp) as max_mslp,
        min(mslp) as min_mslp
        from obs GROUP by hr)
    SELECT o.ts, a.hr::int as hr,
        a.""" + varname + """ from agg1 a JOIN obs o on
        (a.hr = extract(hour from o.ts)
        and a.""" + varname + """ = o.""" + varname2 + """)
        ORDER by a.hr ASC, o.ts DESC
    """, pgconn, params=(nt.sts[station]['tzname'], station,
                         nt.sts[station]['tzname'], tuple(months)),
                  index_col=None)

    y0 = 0.1
    yheight = 0.8
    dy = (yheight / 24.)
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 8))
    ax.set_position([0.12, y0, 0.57, yheight])
    ax.barh(df['hr'], df[varname], align='center')
    ax.set_ylim(-0.5, 23.5)
    ax.set_yticks([0, 4, 8, 12, 16, 20])
    ax.set_yticklabels(['Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'])
    ax.grid(True)
    ax.set_xlim([df[varname].min() - 5,
                 df[varname].max() + 5])
    ax.set_ylabel("Local Time %s" % (nt.sts[station]['tzname'], ),
                  fontproperties=font1)

    fig.text(0.5, 0.93, ("%s [%s] %s-%s\n"
                         "%s [%s]"
                         ) % (nt.sts[station]['name'], station,
                              nt.sts[station]['archive_begin'].year,
                              datetime.date.today().year,
                              PDICT[varname],
                              MDICT[month]),
             ha='center', fontproperties=font1)
    ypos = y0 + (dy / 2.)
    for hr in range(24):
        sdf = df[df['hr'] == hr]
        if sdf.empty:
            continue
        row = sdf.iloc[0]
        fig.text(0.7, ypos,
                 "%3.0f: %s%s" % (row[varname],
                                  row['ts'].strftime("%d %b %Y"),
                                  ("*" if len(sdf.index) > 1 else '')),
                 fontproperties=font0, va='center')
        ypos += dy
    ax.set_xlabel("%s %s, * denotes ties" % (PDICT[varname], UNITS[varname]),
                  fontproperties=font1)

    return plt.gcf(), df


if __name__ == '__main__':
    plotter(dict(over='annual'))
