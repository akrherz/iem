import psycopg2
import calendar
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
from scipy import stats
from collections import OrderedDict

PDICT = OrderedDict([
        ('precip', 'Precipitation'),
        ('avgt', 'Average Temperature'),
        ('high', 'High Temperature'),
        ('low', 'Low Temperature')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This plot presents the daily frequency of the first
    station having a higher value than the second station.
    """
    d['arguments'] = [
        dict(type='station', name='station1', default='IA0200',
             label='Select Station #1:'),
        dict(type='station', name='station2', default='IA2203',
             label='Select Station #2:'),
        dict(type='select', name='pvar', default='high', options=PDICT,
             label='Which variable to plot?'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    station1 = fdict.get('station1', 'IA0200')
    station2 = fdict.get('station2', 'IA2203')
    network1 = fdict.get('network1', 'IACLIMATE')
    network2 = fdict.get('network2', 'IACLIMATE')
    nt1 = NetworkTable(network1)
    nt2 = NetworkTable(network2)
    pvar = fdict.get('pvar', 'high')
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    table1 = "alldata_%s" % (station1[:2], )
    table2 = "alldata_%s" % (station2[:2], )
    df = read_sql("""
    WITH obs1 as (
        SELECT day, high, low, precip, (high+low)/2. as avgt from
        """ + table1 + """ WHERE station = %s),
    obs2 as (
        SELECT day, high, low, precip, (high+low)/2. as avgt from
        """ + table2 + """ WHERE station = %s)

    SELECT extract(doy from o.day) as doy, count(*),
    sum(case when o.high > t.high then 1 else 0 end) as high_hits,
    sum(case when o.low > t.low then 1 else 0 end) as low_hits,
    sum(case when o.precip > t.precip then 1 else 0 end) as precip_hits,
    sum(case when o.avgt > t.avgt then 1 else 0 end) as avgt_hits
    from obs1 o JOIN obs2 t on (o.day = t.day) GROUP by doy ORDER by doy ASC
    """, pgconn, params=(station1, station2), index_col='doy')
    for _v in ['high', 'low', 'avgt', 'precip']:
        df['%s_freq[%%]' % (_v, )] = df["%s_hits" % (_v,)] / df['count'] * 100.

    (fig, ax) = plt.subplots(1, 1)

    ax.bar(df.index.values, df[pvar + '_freq[%]'], fc='r', ec='r')
    ax.axhline(df[pvar + '_freq[%]'].mean())
    ax.grid(True)
    ax.set_ylabel(("Percentage [%%], Ave: %.1f%%"
                   ) % (df[pvar + '_freq[%]'].mean(),))
    ax.set_title(("%s [%s] Daily %s\n%s Than %s [%s]"
                  ) % (nt1.sts[station1]['name'], station1, PDICT[pvar],
                       "Warmer" if pvar != 'precip' else 'Wetter',
                       nt2.sts[station2]['name'], station2))
    ax.set_xlim(0, 366)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])

    return fig, df


if __name__ == '__main__':
    plotter(dict())
