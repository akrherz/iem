"""Two station temperature frequency"""
import calendar
from collections import OrderedDict

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = OrderedDict([
        ('precip', 'Precipitation'),
        ('avgt', 'Average Temperature'),
        ('high', 'High Temperature'),
        ('low', 'Low Temperature')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This plot presents the daily frequency of the
    first station having a higher value than the second station.
    """
    desc['arguments'] = [
        dict(type='station', name='station1', default='IA0200',
             label='Select Station #1:', network='IACLIMATE'),
        dict(type='station', name='station2', default='IATDSM',
             label='Select Station #2:', network='IACLIMATE'),
        dict(type='select', name='pvar', default='high', options=PDICT,
             label='Which variable to plot?'),
        dict(type='float', name='mag', default='1',
             label='By how much warmer [F] or wetter [inch]')
    ]
    return desc


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    station1 = ctx['station1']
    station2 = ctx['station2']
    mag = ctx['mag']
    pvar = ctx['pvar']
    pgconn = get_dbconn('coop')

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
    sum(case when o.high >= (t.high + %s) then 1 else 0 end) as high_hits,
    sum(case when o.low >= (t.low + %s) then 1 else 0 end) as low_hits,
 sum(case when o.precip >= (t.precip + %s) then 1 else 0 end) as precip_hits,
    sum(case when o.avgt >= (t.avgt + %s) then 1 else 0 end) as avgt_hits
    from obs1 o JOIN obs2 t on (o.day = t.day) GROUP by doy ORDER by doy ASC
    """, pgconn, params=(station1, station2, mag, mag, mag, mag),
                  index_col='doy')
    for _v in ['high', 'low', 'avgt', 'precip']:
        df['%s_freq[%%]' % (_v, )] = df["%s_hits" % (_v,)] / df['count'] * 100.

    (fig, ax) = plt.subplots(1, 1)

    ax.bar(df.index.values, df[pvar + '_freq[%]'], fc='r', ec='r')
    ax.axhline(df[pvar + '_freq[%]'].mean())
    ax.grid(True)
    ax.set_ylabel(("Percentage [%%], Ave: %.1f%%"
                   ) % (df[pvar + '_freq[%]'].mean(),))
    v = int(mag) if pvar != 'precip' else round(mag, 2)
    units = " inch" if pvar == 'precip' else r"$^\circ$F"
    ax.set_title(("%s [%s] Daily %s\n%s+%s %s Than %s [%s]"
                  ) % (ctx['_nt1'].sts[station1]['name'], station1,
                       PDICT[pvar],
                       v, units, "Warmer" if pvar != 'precip' else 'Wetter',
                       ctx['_nt2'].sts[station2]['name'], station2))
    ax.set_xlim(0, 366)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])

    return fig, df


if __name__ == '__main__':
    plotter(dict())
