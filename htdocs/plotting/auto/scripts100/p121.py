import psycopg2
from pyiem.network import Table as NetworkTable
import pandas as pd
import datetime
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
    cursor = pgconn.cursor()
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))
    s = nt.sts[station]['archive_begin']
    e = datetime.date.today()

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

    df = pd.DataFrame({'26s': 0, '26f': 0, '24s': 0, '24f': 0,
                       '20s': 0, '20f': 0, '14s': 0, '14f': 0},
                      index=pd.Series(range(s.year, e.year + 1),
                                      name='year'))

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
                df.loc[ts.year, ckey] += 0.5

            # cycled higher
            if cycPos[key] == -1 and high > u:
                # print 'Cycled higher', high, ts
                cycPos[key] = 1
                df.loc[ts.year, ckey] += 0.5

    for yr, row in df.iterrows():
        res += ("%s   %-8i%-8i%-8i%-8i%-8i%-8i%-8i%-8i\n"
                ) % (yr, row['26s'],
                     row['26f'], row['24s'], row['24f'],
                     row['20s'], row['20f'], row['14s'],
                     row['14f'])

    res += ("AVG    %-8.1f%-8.1f%-8.1f%-8.1f%-8.1f%-8.1f%-8.1f%-8.1f\n"
            ) % (df['26s'].mean(),
                 df['26f'].mean(), df['24s'].mean(), df['24f'].mean(),
                 df['20s'].mean(), df['20f'].mean(), df['14s'].mean(),
                 df['14f'].mean())

    return None, df, res

if __name__ == '__main__':
    plotter(dict())
