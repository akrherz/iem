import psycopg2.extras
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """Using long term data, five precipitation bins are
    constructed such that each bin contributes 20% to the annual precipitation
    total.  Using these 5 bins, an individual year's worth of data is
    compared.  With this comparison, you can say that one's years worth of
    departures can be explained by these differences in precipitation bins."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='year', name='year', default=datetime.datetime.now().year,
             label='Year to Highlight:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    IEM = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    today = datetime.datetime.now()
    year = int(fdict.get('year', today.year))
    jdaylimit = 367
    if year == today.year:
        jdaylimit = int(today.strftime("%j"))
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)

    table = "alldata_%s" % (station[:2],)
    endyear = int(datetime.datetime.now().year) + 1
    (fig, ax) = plt.subplots(1, 1)

    cursor.execute("""
        select precip, sum(precip) OVER (ORDER by precip ASC) as rsum,
        sum(precip) OVER () as tsum,
        min(year) OVER () as minyear from """+table+""" where
        station = %s and precip >= 0.01 and extract(doy from day) < %s and
        year < extract(year from now()) ORDER by precip ASC
    """, (station, jdaylimit))
    total = None
    base = None
    bins = [0.01, ]
    minyear = None
    for i, row in enumerate(cursor):
        if i == 0:
            minyear = row['minyear']
            total = row['tsum']
            onefith = total / 5.0
            base = onefith
        if row['rsum'] > base:
            bins.append(row['precip'])
            base += onefith

    normal = total / float(endyear - minyear - 1)
    bins.append(row['precip'])

    yearlybins = np.zeros((endyear-minyear, 5), 'f')
    yearlytotals = np.zeros((endyear-minyear, 5), 'f')

    cursor.execute("""
    SELECT year,
    sum(case when precip >= %s and precip < %s then 1 else 0 end) as bin0,
    sum(case when precip >= %s and precip < %s then 1 else 0 end) as bin1,
    sum(case when precip >= %s and precip < %s then 1 else 0 end) as bin2,
    sum(case when precip >= %s and precip < %s then 1 else 0 end) as bin3,
    sum(case when precip >= %s and precip < %s then 1 else 0 end) as bin4,
    sum(case when precip >= %s and precip < %s then precip else 0 end) as tot0,
    sum(case when precip >= %s and precip < %s then precip else 0 end) as tot1,
    sum(case when precip >= %s and precip < %s then precip else 0 end) as tot2,
    sum(case when precip >= %s and precip < %s then precip else 0 end) as tot3,
    sum(case when precip >= %s and precip < %s then precip else 0 end) as tot4
    from """+table+""" where extract(doy from day) < %s and
    station = %s and precip > 0 and year > 1879 GROUP by year
    """, (bins[0], bins[1], bins[1], bins[2], bins[2], bins[3],
          bins[3], bins[4], bins[4], bins[5],
          bins[0], bins[1], bins[1], bins[2], bins[2], bins[3],
          bins[3], bins[4], bins[4], bins[5],
          jdaylimit, station))
    for row in cursor:
        for i in range(5):
            yearlybins[int(row[0]) - minyear, i] = row['bin%s' % (i, )]
            yearlytotals[int(row[0]) - minyear, i] = row['tot%s' % (i, )]

    avgs = np.average(yearlybins, 0)
    dlast = yearlybins[year-minyear, :]

    bars = ax.bar(np.arange(5) - 0.4, avgs, width=0.4, fc='b', label='Average')
    for i in range(len(bars)):
        ax.text(bars[i].get_x()+0.2, avgs[i] + 1.5, "%.1f" % (avgs[i],),
                ha='center', zorder=2)
        delta = yearlytotals[year-minyear, i] / normal * 100.0 - 20.0
        ax.text(i, max(avgs[i], dlast[i]) + 4,
                "%s%.1f%%" % ("+" if delta > 0 else "", delta,),
                ha='center', color='r',
                bbox=dict(facecolor='white', edgecolor='white'),
                zorder=1)

    bars = ax.bar(np.arange(5), dlast, width=0.4, fc='r',
                  label='%s' % (year,))
    for i in range(len(bars)):
        ax.text(bars[i].get_x()+0.2, dlast[i] + 1.5, "%.0f" % (dlast[i],),
                ha='center')

    ax.text(0.7, 0.8, ("Red text represents %s bin total\nprecip "
                       "departure from average") % (year,),
            transform=ax.transAxes, color='r', ha='center', va='top',
            bbox=dict(facecolor='white', edgecolor='white'))
    ax.legend()
    ax.grid(True)
    ax.set_ylabel("Days")
    ax.text(0.5, -0.05, ("Precipitation Bins [inch], split into equal 20%%"
                         " by rain volume (%.2fin)") % (normal / 5.0, ),
            transform=ax.transAxes, va='top', ha='center')
    addl = ""
    if jdaylimit < 377:
        addl = " thru %s" % (today.strftime("%-d %b"), )
    ax.set_title("%s [%s] [%s-%s]\nDaily Precipitation Contributions%s" % (
                nt.sts[station]['name'], station, minyear, endyear-2, addl))
    ax.set_xticks(np.arange(0, 5))
    xlabels = []
    for i in range(5):
        xlabels.append("%.2f-%.2f" % (bins[i], bins[i+1]))
    ax.set_xticklabels(xlabels)

    return fig
