import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime


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
    s = nt.sts[station]['archive_begin']
    e = datetime.date.today()
    YEARS = e.year - s.year + 1

    res = """\
# IEM Climodat http://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# SEASONAL TEMPERATURE CYCLES PER YEAR
# 1 CYCLE IS A TEMPERATURE VARIATION FROM A VALUE BELOW A THRESHOLD
#   TO A VALUE EXCEEDING A THRESHOLD.  THINK OF IT AS FREEZE/THAW CYCLES
#  FIRST DATA COLUMN WOULD BE FOR CYCLES EXCEEDING 26 AND 38 DEGREES F
THRES  26-38   26-38   24-40   24-40   20-44   20-44   14-50   14-50
YEAR   SPRING  FALL    SPRING  FALL    SPRING  FALL    SPRING  FALL
""" % (datetime.date.today().strftime("%d %b %Y"),
       nt.sts[station]['archive_begin'].date(), datetime.date.today(), station,
       nt.sts[station]['name'])

    data = {}
    for yr in range(s.year, e.year + 1):
        data[yr] = {'26s': 0, '26f': 0, '24s': 0, '24f': 0,
                    '20s': 0, '20f': 0, '14s': 0, '14f': 0}

    prs = [[26, 38], [24, 40], [20, 44], [14, 50]]

    cycPos = {'26s': -1, '24s': -1, '20s': -1, '14s': -1}

    cursor.execute("""SELECT day, high, low from """+table+"""
    WHERE station = %s and high is not null and low is not null
    ORDER by day ASC""", (station, ))
    for row in cursor:
        ts = row[0]
        high = int(row[1])
        low = int(row[2])

        for pr in prs:
            l, u = pr
            key = '%ss' % (l, )
            ckey = '%ss' % (l, )
            if ts.month >= 7:
                ckey = '%sf' % (l, )

            # cycles lower
            if cycPos[key] == 1 and low < l:
                # print 'Cycled lower', low, ts
                cycPos[key] = -1
                data[ts.year][ckey] += 0.5

            # cycled higher
            if cycPos[key] == -1 and high > u:
                # print 'Cycled higher', high, ts
                cycPos[key] = 1
                data[ts.year][ckey] += 0.5

    s26 = 0
    f26 = 0
    s24 = 0
    f24 = 0
    s20 = 0
    f20 = 0
    s14 = 0
    f14 = 0
    for yr in range(s.year, e.year + 1):
        s26 += data[yr]['26s']
        f26 += data[yr]['26f']
        s24 += data[yr]['24s']
        f24 += data[yr]['24f']
        s20 += data[yr]['20s']
        f20 += data[yr]['20f']
        s14 += data[yr]['14s']
        f14 += data[yr]['14f']
        res += ("%s   %-8i%-8i%-8i%-8i%-8i%-8i%-8i%-8i\n"
                   "") % (yr, data[yr]['26s'],
                          data[yr]['26f'], data[yr]['24s'], data[yr]['24f'],
                          data[yr]['20s'], data[yr]['20f'], data[yr]['14s'],
                          data[yr]['14f'])

    res += ("AVG    %-8.1f%-8.1f%-8.1f%-8.1f%-8.1f%-8.1f%-8.1f%-8.1f\n"
               "") % (s26/YEARS, f26/YEARS, s24/YEARS, f24/YEARS, s20/YEARS,
                      f20/YEARS, s14/YEARS, f14/YEARS)

    return None, None, res

if __name__ == '__main__':
    plotter(dict())
