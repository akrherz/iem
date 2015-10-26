import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
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

    station = fdict.get('station', 'IA0200')

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))
    df = read_sql("""
    SELECT day, precip from """+table+""" WHERE station = %s
    ORDER by precip DESC LIMIT 30
    """, pgconn, params=(station,), index_col=None)

    res = ("""\
# IEM Climodat http://mesonet.agron.iastate.edu/climodat/
# Report Generated:
# Climate Record:  ->  (data after  is preliminary)
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# Top 30 single day rainfalls
 MONTH  DAY  YEAR   AMOUNT
""" % (station, nt.sts[station]['name']))

    for _, row in df.iterrows():
        res += "%4i%7i%6i%9.2f\n" % (row['day'].month, row['day'].day,
                                     row['day'].year, row["precip"])

    return None, df, res

if __name__ == '__main__':
    plotter(dict())
