import psycopg2.extras
import numpy as np
import datetime
import pandas as pd
from scipy import stats
from pyiem.network import Table as NetworkTable


PDICT = {'end_summer': 'End of Summer', 'start_summer': 'Start of Summer'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart presents the start or end date of the
    warmest 91 day period each year.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='select', name='which', default='end_summer',
             label='Which value to plot:', options=PDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    IEM = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

    which = fdict.get('which', 'end_summer')
    station = fdict.get('station', 'IA0200')
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)

    table = "alldata_%s" % (station[:2],)

    cursor.execute("""
    select year, extract(doy from day) as d from
        (select day, year, rank() OVER (PARTITION by year ORDER by avg DESC)
        from
            (select day, year, avg((high+low)/2.) OVER
            (ORDER by day ASC rows 91 preceding) from """ + table + """
            where station = %s) as foo) as foo2 where rank = 1
            ORDER by day DESC
    """, (station, ))
    years = []
    maxsday = []
    today = datetime.date.today()
    today_doy = int(today.strftime("%j"))
    delta = 0 if which == 'end_summer' else 91
    for row in cursor:
        if row['year'] == today.year and (row['d'] + 10) > today_doy:
            continue
        maxsday.append(row['d'] - delta)
        years.append(row['year'])

    df = pd.DataFrame(dict(year=pd.Series(years),
                           doy=pd.Series(maxsday)))
    maxsday = np.array(maxsday)

    (fig, ax) = plt.subplots(1, 1)
    ax.scatter(years, maxsday)
    ax.grid(True)
    ax.set_ylabel("%s Date" % ('End' if delta == 0 else 'Start',))
    ax.set_title(("%s [%s] %s\n"
                  "%s Date of Warmest (Avg Temp) 91 Day Period"
                  ) % (nt.sts[station]['name'], station, PDICT.get(which),
                       'End' if delta == 0 else 'Start'))

    yticks = []
    yticklabels = []
    for i in np.arange(min(maxsday)-5, max(maxsday)+5, 1):
        ts = datetime.datetime(2000, 1, 1) + datetime.timedelta(days=i)
        if ts.day in [1, 8, 15, 22, 29]:
            yticks.append(i)
            yticklabels.append(ts.strftime("%-d %b"))
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)

    h_slope, intercept, r_value, _, _ = stats.linregress(years, maxsday)
    ax.plot(years, h_slope * np.array(years) + intercept, lw=2, color='r')

    avgd = datetime.datetime(2000, 1, 1) + datetime.timedelta(
                                                days=int(np.average(maxsday)))
    ax.text(0.1, 0.03, "Avg Date: %s, slope: %.2f days/century, R$^2$=%.2f" % (
            avgd.strftime("%-d %b"), h_slope * 100., r_value ** 2),
            transform=ax.transAxes, va='bottom')
    ax.set_xlim(min(years)-1, max(years)+1)
    ax.set_ylim(min(maxsday)-5, max(maxsday)+5)

    return fig, df
