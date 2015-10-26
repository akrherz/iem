import psycopg2
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
    cursor = pgconn.cursor()

    station = fdict.get('station', 'IA0200')

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))

    res = ("# THESE ARE THE HEAT STRESS VARIABLES FOR STATION #  %s\n"
           ) % (station,)

    s = nt.sts[station]['archive_begin']
    e = datetime.date.today().year + 1
    today = datetime.date.today()

    monthlyCount = {}
    monthlyIndex = {}
    now = s
    for year in range(s.year, e):
        for month in range(1, 13):
            now = datetime.date(year, month, 1)
            monthlyCount[now] = 0
            monthlyIndex[now] = 0

    cursor.execute("""
            SELECT year, month, high from """+table+""" WHERE
            station = %s and high > 86
    """, (station,))
    for row in cursor:
        ts = datetime.date(row[0], row[1], 1)
        monthlyCount[ts] += 1
        monthlyIndex[ts] += int(row[2]) - 86

    monthlyAveCnt = {}
    monthlyAveIndex = {}
    for mo in range(5, 10):
        monthlyAveCnt[mo] = 0
        monthlyAveIndex[mo] = 0

    res += """             # OF DAYS MAXT >86              ACCUMULATED (MAXT - 86 )
 YEAR   MAY  JUNE  JULY   AUG  SEPT TOTAL      MAY  JUNE  JULY   AUG  SEPT TOTAL\n"""

    yrCnt = 0
    for yr in range(s.year, e):
        yrCnt += 1
        res += ("%5s" % (yr,))
        totCnt = 0
        for mo in range(5, 10):
            ts = datetime.date(yr, mo, 1)
            if (ts >= today):
                res += ("%6s" % ("M",))
                continue
            totCnt += monthlyCount[ts]
            monthlyAveCnt[mo] += monthlyCount[ts]
            res += ("%6i" % (monthlyCount[ts], ))
        res += ("%6i   " % (totCnt,))
        totInd = 0
        for mo in range(5, 10):
            ts = datetime.date(yr, mo, 1)
            if (ts >= today):
                res += ("%6s" % ("M",))
                continue
            totInd += monthlyIndex[ts]
            monthlyAveIndex[mo] += monthlyIndex[ts]
            res += ("%6i" % (monthlyIndex[ts], ))
        res += ("%6i\n" % (totInd,))

    res += (" **************************************************************************************\n")

    res += ("MEANS")
    tot = 0
    for mo in range(5, 10):
        val = float(monthlyAveCnt[mo]) / float(yrCnt)
        tot += val
        res += ("%6.1f" % (val, ))
    res += ("%6.1f   " % (tot,))
    tot = 0
    for mo in range(5, 10):
        val = float(monthlyAveIndex[mo]) / float(yrCnt)
        tot += val
        res += ("%6.1f" % (val, ))
    res += ("%6.1f\n" % (tot, ))

    return None, None, res

if __name__ == '__main__':
    plotter(dict())
