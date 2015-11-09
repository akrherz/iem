import psycopg2
from pandas.io.sql import read_sql
from collections import OrderedDict
from pyiem.network import Table as NetworkTable

PDICT = OrderedDict([
    ('avg_high', 'Average High Temperature'),
    ('avg_low', 'Average Low Temperature'),
    ('avg_temp', 'Average Temperature'),
    ('max_high', 'Maximum Daily High'),
    ('max_low', 'Maximum Daily Low'),
    ('total_precip', 'Total Precipitation'),
    ])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart compares yearly summaries between two
    long term climate sites."""
    d['arguments'] = [
        dict(type='select', options=PDICT, name='var',
             label='Select Variable to Plot', default='avg_temp'),
        dict(type='station', name='station1', default='IA2203',
             label='Select First Station:'),
        dict(type='station', name='station2', default='IA0200',
             label='Select Secont Station:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station1 = fdict.get('station1', 'IA2203').upper()
    station2 = fdict.get('station2', 'IA0200').upper()
    table1 = "alldata_%s" % (station1[:2], )
    table2 = "alldata_%s" % (station2[:2], )
    nt1 = NetworkTable("%sCLIMATE" % (station1[:2],))
    nt2 = NetworkTable("%sCLIMATE" % (station2[:2],))
    varname = fdict.get('var', 'avg_temp')

    df = read_sql("""WITH one as (
      SELECT year, sum(precip) as one_total_precip,
      avg(high) as one_avg_high, avg(low) as one_avg_low,
      avg((high+low)/2.) as one_avg_temp, max(high) as one_max_high,
      min(low) as one_min_low from """ + table1 + """ WHERE
      station = %s GROUP by year),
    two as (
      SELECT year, sum(precip) as two_total_precip,
      avg(high) as two_avg_high, avg(low) as two_avg_low,
      avg((high+low)/2.) as two_avg_temp, max(high) as two_max_high,
      min(low) as two_min_low from """ + table2 + """ WHERE
      station = %s GROUP by year
    )

    SELECT o.year, one_total_precip, one_avg_high, one_avg_low,
    one_avg_temp, one_max_high, one_min_low, two_total_precip, two_avg_high,
    two_avg_low, two_avg_temp, two_max_high, two_min_low from one o JOIN two t
    on (o.year = t.year) ORDER by o.year ASC
    """, pgconn, params=(station1, station2), index_col='year')
    df['one_station'] = station1
    df['two_station'] = station2
    for col in ['total_precip', 'avg_high', 'avg_low', 'max_high', 'min_low',
                'avg_temp']:
        df['diff_'+col] = df['one_'+col] - df['two_'+col]

    (fig, ax) = plt.subplots(1, 1)
    color_above = 'b' if varname in ['total_precip', ] else 'r'
    color_below = 'r' if color_above == 'b' else 'b'

    bars = ax.bar(df.index, df['diff_'+varname], fc=color_above,
                  ec=color_above)
    for bar, val in zip(bars, df['diff_'+varname].values):
        if val < 0:
            bar.set_facecolor(color_below)
            bar.set_edgecolor(color_below)

    ax.set_title(("Yearly %s [%s] %s\nminus [%s] %s"
                  ) % (PDICT[varname], station1,
                       nt1.sts[station1]['name'], station2,
                       nt2.sts[station2]['name']))
    units = 'inch' if varname in ['total_precip', ] else 'F'
    lbl = 'wetter' if units == 'inch' else 'warmer'
    wins = len(df[df['diff_'+varname] > 0].index)
    ax.text(0.5, 0.95, "%s %s (%s/%s)" % (nt1.sts[station1]['name'], lbl,
                                          wins, len(df.index)),
            transform=ax.transAxes, ha='center')
    wins = len(df[df['diff_'+varname] < 0].index)
    ax.text(0.5, 0.05, "%s %s (%s/%s)" % (nt1.sts[station2]['name'], lbl,
                                          wins, len(df.index)),
            transform=ax.transAxes, ha='center')
    ax.axhline(df['diff_'+varname].mean(), lw=2, color='k')
    ax.set_ylabel("%s [%s] Avg: %.2f" % (PDICT[varname], units,
                                         df['diff_'+varname].mean()))
    ax.grid(True)
    ax.set_xlim(df.index.min()-1, df.index.max()+1)
    ymax = df['diff_'+varname].abs().max() * 1.1
    ax.set_ylim(0 - ymax, ymax)
    return fig, df

if __name__ == '__main__':
    plotter(dict())
