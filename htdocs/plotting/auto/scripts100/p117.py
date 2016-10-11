import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime
import numpy as np
from pyiem.util import get_autoplot_context


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['report'] = True
    d['description'] = """ """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))
    res = ("# IEM Climodat http://mesonet.agron.iastate.edu/climodat/\n"
           "# Report Generated: %s\n"
           "# Climate Record: %s -> %s\n"
           "# Site Information: [%s] %s\n"
           "# Contact Information: Daryl Herzmann "
           "akrherz@iastate.edu 515.294.5978\n"
           ) % (datetime.date.today().strftime("%d %b %Y"),
                nt.sts[station]['archive_begin'].date(), datetime.date.today(),
                station, nt.sts[station]['name'])
    res += ("# THESE ARE THE HEAT STRESS VARIABLES FOR STATION #  %s\n"
            ) % (station,)

    s = nt.sts[station]['archive_begin']
    e = datetime.date.today().year + 1

    df = read_sql("""
        SELECT year, month, sum(case when high > 86 then 1 else 0 end) as days,
        sum(case when high > 86 then high - 86 else 0 end) as sdd
        from """+table+""" WHERE
        station = %s GROUP by year, month
    """, pgconn, params=(station,), index_col=None)
    sdd = df.pivot('year', 'month', 'sdd')
    days = df.pivot('year', 'month', 'days')
    df = sdd.join(days, lsuffix='sdd', rsuffix='days')

    res += ("             # OF DAYS MAXT >86                     "
            "ACCUMULATED (MAXT - 86 )\n"
            " YEAR   MAY  JUNE  JULY   AUG  SEPT TOTAL      "
            "MAY  JUNE  JULY   AUG  SEPT TOTAL\n")

    yrCnt = 0
    for yr in range(s.year, e):
        yrCnt += 1
        res += ("%5s" % (yr,))
        total = 0
        for mo in range(5, 10):
            val = df.at[yr, "%sdays" % (mo,)]
            if np.isnan(val):
                res += ("%6s" % ("M",))
            else:
                res += ("%6i" % (val, ))
                total += val
        res += ("%6i   " % (total,))
        total = 0
        for mo in range(5, 10):
            val = df.at[yr, "%ssdd" % (mo,)]
            if np.isnan(val):
                res += ("%6s" % ("M",))
            else:
                res += ("%6i" % (val, ))
                total += val
        res += ("%6i   \n" % (total,))

    res += (" **************************************************************"
            "************************\n")

    res += ("MEANS")
    tot = 0
    for mo in range(5, 10):
        val = df["%sdays" % (mo,)].mean()
        tot += val
        res += ("%6.1f" % (val, ))
    res += ("%6.1f   " % (tot,))
    tot = 0
    for mo in range(5, 10):
        val = df["%ssdd" % (mo,)].mean()
        tot += val
        res += ("%6.1f" % (val, ))
    res += ("%6.1f\n" % (tot, ))

    return None, df, res

if __name__ == '__main__':
    plotter(dict())
