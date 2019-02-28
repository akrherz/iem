"""Days per year"""
import datetime

from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['report'] = True
    desc['description'] = """ """
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station', network='IACLIMATE'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station'].upper()

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))
    df = read_sql("""
     SELECT year, count(low) from """+table+""" WHERE
     station = %s and low >= 32
    and year < %s GROUP by year ORDER by year ASC
    """, pgconn, params=(station, datetime.date.today().year), index_col=None)

    res = """\
# IEM Climodat https://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# OF DAYS EACH YEAR WHERE MIN >=32 F
""" % (datetime.date.today().strftime("%d %b %Y"),
       nt.sts[station]['archive_begin'].date(), datetime.date.today(), station,
       nt.sts[station]['name'])

    for _, row in df.iterrows():
        res += "%s %3i\n" % (row['year'], row['count'])

    res += "MEAN %3i\n" % (df['count'].mean(),)

    return None, df, res


if __name__ == '__main__':
    plotter(dict())
