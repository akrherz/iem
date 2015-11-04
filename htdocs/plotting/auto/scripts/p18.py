import psycopg2.extras
from pyiem.network import Table as NetworkTable
import datetime
import numpy as np
from pandas.io.sql import read_sql


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    ts = datetime.date.today() - datetime.timedelta(days=365)
    d['data'] = True
    d['description'] = """This chart displays a simple time series of
    observed air temperatures for a location of your choice.  For sites in the
    US, the daily high and low temperature climatology is presented as a
    filled bar for each day plotted."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
        dict(type='date', name='sdate', default=ts.strftime("%Y/%m/%d"),
             label='Start Date of Plot:',
             min="1951/01/01"),  # Comes back to python as yyyy-mm-dd
        dict(type='text', name='days', default='365',
             label='Days to Plot'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    nt = NetworkTable(network)
    sdate = datetime.datetime.strptime(fdict.get('sdate', '2000-01-01'),
                                       '%Y-%m-%d')
    days = int(fdict.get('days', 365))
    edate = sdate + datetime.timedelta(days=days)
    today = datetime.datetime.today()
    if edate > today:
        edate = today
        days = (edate - sdate).days

    climo = {}
    ccursor.execute("""
    SELECT valid, high, low from ncdc_climate81 where station = %s
    """, (nt.sts[station]['ncdc81'],))
    for row in ccursor:
        climo[row[0].strftime("%m%d")] = dict(high=row[1], low=row[2])

    df = read_sql("""
     SELECT valid, tmpf from alldata WHERE station = %s
     and valid > %s and valid < %s ORDER by valid ASC
    """, ASOS, params=(station, sdate, sdate + datetime.timedelta(days=days)),
                  index_col='valid')

    (fig, ax) = plt.subplots(1, 1)

    xticks = []
    xticklabels = []
    now = sdate
    cdates = []
    chighs = []
    clows = []
    while now <= edate:
        cdates.append(now)
        chighs.append(climo[now.strftime("%m%d")]['high'])
        clows.append(climo[now.strftime("%m%d")]['low'])
        if now.day == 1 or (now.day % 12 == 0 and days < 180):
            xticks.append(now)
            fmt = "%-d"
            if now.day == 1:
                fmt = "%-d\n%b"
            xticklabels.append(now.strftime(fmt))

        now += datetime.timedelta(days=1)

    chighs = np.array(chighs)
    clows = np.array(clows)

    ax.bar(cdates, chighs - clows, bottom=clows, fc='lightblue',
           ec='lightblue', label="Daily Climatology")
    ax.plot(df.index.values, df['tmpf'], color='r', label='Hourly Obs')
    ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(sdate, edate)
    ax.set_ylim(top=df['tmpf'].max() + 15.)
    ax.legend(loc=2, ncol=2)
    ax.axhline(32, linestyle='-.')
    ax.grid(True)
    ax.set_title(("%s [%s]\nAir Temperature Timeseries %s - %s"
                  ) % (nt.sts[station]['name'], station,
                       sdate.strftime("%d %b %Y"),
                       edate.strftime("%d %b %Y")))

    return fig, df
