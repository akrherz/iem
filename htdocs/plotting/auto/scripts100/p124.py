import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime
import numpy as np


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
    cursor = pgconn.cursor()

    station = fdict.get('station', 'IA0200')

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))
    CATS = np.array([0.01, 0.5, 1., 2., 3., 4.])

    startyear = nt.sts[station]['archive_begin'].year
    years = datetime.date.today().year - startyear
    # 0.01, 0.5, 1, 2, 3, 4
    data = np.zeros((13, years+1, 6), 'i')
    cursor.execute("""SELECT year, precip, month from """+table+"""
    WHERE station = '%s'""" % (station, ))
    for row in cursor:
        precip = float(row[1])
        if precip <= 0:
            continue
        offset = int(row[0]) - startyear
        data[0, offset, :] += np.where(precip >= CATS, 1, 0)
        data[int(row[2]), offset, :] += np.where(precip >= CATS, 1, 0)
    res = """\
# IEM Climodat http://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# Number of days per year with precipitation at or above threshold [inch]
# Partitioned by month of the year, 'ANN' represents the entire year
""" % (datetime.date.today().strftime("%d %b %Y"),
       nt.sts[station]['archive_begin'].date(), datetime.date.today(), station,
       nt.sts[station]['name'])

    for c in range(len(CATS)):
        res += """YEAR %4.2f JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC ANN
""" % (CATS[c],)
        for yr in range(startyear, datetime.date.today().year + 1):
            res += "%s %4.2f " % (yr, CATS[c])
            for mo in range(1, 13):
                res += "%3.0f " % (data[mo, yr-startyear, c], )
            res += "%3.0f\n" % (data[0, yr-startyear, c], )

    return None, None, res

if __name__ == '__main__':
    plotter(dict())
