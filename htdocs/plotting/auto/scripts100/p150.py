import psycopg2
import calendar
import pytz
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime
from collections import OrderedDict

PDICT = {'00': '00 UTC', '12': '12 UTC'}
PDICT2 = {
    'none': 'No Comparison Limit (All Soundings)',
    'month': 'Month of the Selected Profile'}
PDICT3 = OrderedDict([
    ('tmpc', 'Air Temperature (C)'),
    ('dwpc', 'Dew Point (C)'),
    ('hght', 'Height (m)'),
    ('smps', 'Wind Speed (mps)')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This plot presents percentiles of observations from
    a given sounding profile against the long term record for the site.
    """
    today = datetime.date.today()
    d['arguments'] = [
        dict(type='networkselect', name='station', network='RAOB',
             default='KOAX', label='Select Station:'),
        dict(type='date', name='date', default=today.strftime("%Y/%m/%d"),
             min='1946/01/01',
             label='Date of the Sounding:'),
        dict(type='select', name='hour', default='00', options=PDICT,
             label='Which Sounding from Above Date:'),
        dict(type='select', name='which', default='month', options=PDICT2,
             label='Compare this sounding against:'),
        dict(type='select', name='var', default='tmpc', options=PDICT3,
             label='Which Sounding Variable to Plot:'),

    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    station = fdict.get('station', 'KOAX')
    varname = fdict.get('var', 'tmpc')
    network = 'RAOB'
    ts = datetime.datetime.strptime(fdict.get('date', '2015-12-25'),
                                    '%Y-%m-%d')
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    hour = int(fdict.get('hour', '00'))
    which = fdict.get('which', 'month')
    ts = ts.replace(hour=hour)
    vlimit = ''
    if which == 'month':
        vlimit = (" and extract(month from f.valid) = %s "
                  ) % (ts.month,)
    nt = NetworkTable(network)
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')

    df = read_sql("""
    with data as (
        select f.valid, p.pressure, count(*) OVER (PARTITION by p.pressure),
        min(valid) OVER () as min_valid, max(valid) OVER () as max_valid,
        p.tmpc,
        rank() OVER (PARTITION by p.pressure ORDER by p.tmpc ASC) as tmpc_rank,
        min(p.tmpc) OVER (PARTITION by p.pressure) as tmpc_min,
        max(p.tmpc) OVER (PARTITION by p.pressure) as tmpc_max,
        p.dwpc,
        rank() OVER (PARTITION by p.pressure ORDER by p.dwpc ASC) as dwpc_rank,
        min(p.dwpc) OVER (PARTITION by p.pressure) as dwpc_min,
        max(p.dwpc) OVER (PARTITION by p.pressure) as dwpc_max,
        p.height as hght,
        rank() OVER (
            PARTITION by p.pressure ORDER by p.height ASC) as hght_rank,
        min(p.height) OVER (PARTITION by p.pressure) as hght_min,
        max(p.height) OVER (PARTITION by p.pressure) as hght_max,
        p.smps,
        rank() OVER (PARTITION by p.pressure ORDER by p.smps ASC) as smps_rank,
        min(p.smps) OVER (PARTITION by p.pressure) as smps_min,
        max(p.smps) OVER (PARTITION by p.pressure) as smps_max
        from raob_flights f JOIN raob_profile p on (f.fid = p.fid)
        WHERE f.station = %s
        and extract(hour from f.valid at time zone 'UTC') = %s
        """ + vlimit + """
        and p.pressure in (925, 850, 700, 500, 400, 300, 250, 200,
        150, 100, 70, 50, 10))

    select * from data where valid = %s ORDER by pressure DESC
    """, pgconn, params=(station, hour, ts),
                  index_col='pressure')
    for key in PDICT3.keys():
        df[key+'_percentile'] = df[key+'_rank'] / df['count'] * 100.

    ax = plt.axes([0.1, 0.1, 0.65, 0.75])
    bars = ax.barh(range(len(df.index)), df[varname+'_percentile'],
                   align='center')
    y2labels = []
    fmt = '%.1f' if varname not in ['hght', ] else '%.0f'
    for i, bar in enumerate(bars):
        ax.text(bar.get_width() + 1, i, fmt % (bar.get_width(),),
                va='center', bbox=dict(color='white'))
        y2labels.append((fmt + ' (' + fmt + ' ' + fmt + ')'
                         ) % (df.iloc[i][varname],
                              df.iloc[i][varname+"_min"],
                              df.iloc[i][varname+"_max"]))
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(['%.0f' % (a, ) for a in df.index.values])
    ax.set_ylim(-0.5, len(df.index) - 0.5)
    ax.set_xlabel("Percentile [100 = highest]")
    ax.set_ylabel("Mandatory Pressure Level")
    plt.gcf().text(0.5, 0.9,
                   ("%s %s %s Sounding\n"
                    "(%s-%s) Percentile Ranks (%s) for %s"
                    ) % (station, nt.sts[station]['name'],
                         ts.strftime("%Y/%m/%d %H UTC"),
                         df.iloc[0]['min_valid'].year,
                         df.iloc[0]['max_valid'].year,
                         ("All Year" if which == 'none'
                          else calendar.month_name[ts.month]),
                         PDICT3[varname]),
                   ha='center', va='bottom')
    ax.grid(True)
    ax.set_xticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_xlim(0, 110)
    ax.text(1.02, 1, 'Ob  (Min  Max)', transform=ax.transAxes)

    ax2 = ax.twinx()
    ax2.set_ylim(-0.5, len(df.index) - 0.5)
    ax2.set_yticks(range(len(df.index)))
    ax2.set_yticklabels(y2labels)
    return plt.gcf(), df


if __name__ == '__main__':
    plotter(dict())
