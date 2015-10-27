import psycopg2.extras
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime


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
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))
    res = """\
# IEM Climodat http://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# Number of days exceeding given temperature thresholds
# -20, -10, 0, 32 are days with low temperature at or below value
# 50, 70, 80, 93, 100 are days with high temperature at or above value
""" % (datetime.date.today().strftime("%d %b %Y"),
       nt.sts[station]['archive_begin'].date(), datetime.date.today(), station,
       nt.sts[station]['name'])
    res += ("%s %4s %4s %4s %4s %4s %4s %4s %4s %4s\n"
            "") % ('YEAR', -20, -10, 0, 32, 50, 70, 80, 93, 100)

    cursor.execute("""SELECT year,
       sum(case when low <= -20 THEN 1 ELSE 0 END) as m20,
       sum(case when low <= -10 THEN 1 ELSE 0 END) as m10,
       sum(case when low <=  0 THEN 1 ELSE 0 END) as m0,
       sum(case when low <=  32 THEN 1 ELSE 0 END) as m32,
       sum(case when high >= 50 THEN 1 ELSE 0 END) as e50,
       sum(case when high >= 70 THEN 1 ELSE 0 END) as e70,
       sum(case when high >= 80 THEN 1 ELSE 0 END) as e80,
       sum(case when high >= 93 THEN 1 ELSE 0 END) as e93,
       sum(case when high >= 100 THEN 1 ELSE 0 END) as e100
       from """+table+""" WHERE station = '%s'
       GROUP by year ORDER by year ASC
    """ % (station,))

    for row in cursor:
        res += ("%(year)4i %(m20)4i %(m10)4i %(m0)4i %(m32)4i %(e50)4i "
                "%(e70)4i %(e80)4i %(e93)4i %(e100)4i\n") % row

    return None, None, res

if __name__ == '__main__':
    plotter(dict())
