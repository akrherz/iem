import psycopg2
from pandas.io.sql import read_sql
import numpy as np
from pyiem import network
import calendar
from collections import OrderedDict

PDICT = OrderedDict(
    [('min_range', 'Minimum Daily High to Low Temperature Range'),
     ('max_range', 'Maximum Daily High to Low Temperature Range'),
     ('max_high', 'Maximum Daily High Temperature'),
     ('max_low', 'Maximum Daily Low Temperature'),
     ('min_high', 'Minimum Daily High Temperature'),
     ('min_low', 'Minimum Daily Low Temperature'),
     ('max_precip', 'Maximum Daily Precipitation'),
     ('max_snow', 'Maximum Daily Snowfall'),
     ])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot displays the dates with the monthly
    record of your choice displayed. In the case of ties, only the most
    recent occurence is shown."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='select', name='var', default='min_range',
             label='Select Variable', options=PDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA2203')
    varname = fdict.get('var', 'min_range')
    if varname not in PDICT:
        return "Invalid var specified..."
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    tokens = varname.split("_")
    orderer = "(high - low)"
    if tokens[1] != 'range':
        orderer = tokens[1]

    if tokens[0] == 'min':
        orderer += " ASC"
    else:
        orderer += " DESC"
    df = read_sql("""
    WITH ranks as (
        SELECT month, day, high, low, precip, snow,
        rank() OVER (PARTITION by month ORDER by """ + orderer + """ NULLS LAST)
        from """ + table + """ WHERE station = %s)

    select month, to_char(day, 'Mon dd, YYYY') as dd, high, low, precip, snow,
    (high - low) as range from ranks
    WHERE rank = 1 ORDER by month ASC, day DESC
    """, pgconn, params=(station, ), index_col='month')
    labels = []
    ranges = []
    months = []
    for i, row in df.iterrows():
        if i in months:
            if labels[-1].endswith("*"):
                continue
            labels[-1] += " *"
            continue
        months.append(i)
        if tokens[1] == 'range':
            labels.append("%s (%s/%s) - %s" % (row[tokens[1]], row['high'],
                                               row['low'],
                                               row['dd']))
        else:
            labels.append("%s - %s" % (row[tokens[1]], row['dd']))
        ranges.append(row[tokens[1]])

    (fig, ax) = plt.subplots(1, 1)

    ax.barh(np.arange(1, 13) - 0.4, ranges)
    ax.set_yticklabels(calendar.month_name)
    ax.set_yticks(range(0, 13))
    ax.set_ylim(0, 13)
    ax.set_xlabel(("Date most recently set/tied shown, "
                  "* indicates ties are present"))
    fig.text(0.5, 0.99, "%s [%s]\n%s by Month" % (
                  nt.sts[station]['name'], station, PDICT[varname]),
             transform=ax.transAxes, ha='center', fontsize=14, va='top')

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
    ax.grid(True)

    ax2 = ax.twinx()
    ax2.set_yticks(range(1, 13))
    ax2.set_yticklabels(labels)
    ax2.set_position([box.x0, box.y0, box.width * 0.7, box.height])
    ax2.set_ylim(0, 13)

    return fig, df

if __name__ == '__main__':
    plotter({'var': 'max_snow'})
