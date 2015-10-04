import psycopg2.extras
import numpy as np
from pyiem import network
from scipy import stats
import calendar
import pandas as pd

PDICT = {'above': 'First Spring/Last Fall Temperature Above Threshold',
         'below': 'Last Spring/First Fall Temperature Below Threshold'}

PDICT2 = {'low': 'Low Temperature',
          'high': 'High Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='select', name='direction', default='below',
             label='Threshold Direction', options=PDICT),
        dict(type='select', name='varname', default='low',
             label='Daily High or Low Temperature?', options=PDICT2),
        dict(type='text', name='threshold', default='32',
             label='Enter Threshold Temperature:'),
        dict(type='year', name='year', default=1893,
             label='Start Year of Plot'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    threshold = int(fdict.get('threshold', 32))
    direction = fdict.get('direction', 'below')
    varname = fdict.get('varname', 'low')
    startyear = int(fdict.get('year', 1893))
    if varname not in PDICT2:
        varname = 'low'

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    sql = """select year,
     max(case when """+varname+""" < %s and month < 7
         then extract(doy from day) else 0 end) as spring,
     min(case when """+varname+""" < %s and month > 6
         then extract(doy from day) else 388 end) as fall
    from """+table+""" where station = %s
    GROUP by year ORDER by year ASC"""
    if direction == 'above':
        sql = """select year,
             min(case when """+varname+""" > %s and month < 7
                 then extract(doy from day) else 183 end) as spring,
             max(case when """+varname+""" > %s and month > 6
                 then extract(doy from day) else 183 end) as fall
            from """+table+""" where station = %s
            GROUP by year ORDER by year ASC"""

    ccursor.execute(sql, (threshold, threshold, station))
    rows = []
    for row in ccursor:
        if row['year'] < startyear:
            continue
        if row['fall'] > 366:
            continue
        if row['fall'] == 183 and row['spring'] == 183:
            continue
        rows.append(dict(year=row['year'], spring=row['spring'],
                         fall=row['fall']))

    df = pd.DataFrame(rows)
    years = np.array(df['year'])
    spring = np.array(df['spring'])
    fall = np.array(df['fall'])

    s_slp, s_int, s_r, _, _ = stats.linregress(years, spring)
    f_slp, f_int, f_r, _, _ = stats.linregress(years, fall)

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(years, fall-spring, bottom=spring, ec='tan', fc='tan', zorder=1)
    ax.plot(years, years * s_slp + s_int, lw=3,
            zorder=2, label=r"%.2f $\frac{days}{100y}$ R$^2$=%.2f" % (
                                                        s_slp * 100.,
                                                        s_r ** 2))
    ax.plot(years, years * f_slp + f_int, lw=3,
            zorder=2, label=r"%.2f $\frac{days}{100y}$ R$^2$=%.2f" % (
                                                        f_slp * 100.,
                                                        f_r ** 2))
    ax.grid(True)
    title = PDICT.get(direction, '').replace('Temperature',
                                             PDICT2.get(varname))
    ax.set_title(("[%s] %s\n"
                  "%s %s$^\circ$F"
                  ) % (station, nt.sts[station]['name'], title, threshold))
    ax.legend(ncol=2, fontsize=14, labelspacing=2)
    ax.set_yticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_yticklabels(calendar.month_abbr[1:])
    ax.set_ylim(min(spring) - 5, max(fall) + 40)
    ax.set_xlim(min(years)-1, max(years)+1)
    return fig, df
