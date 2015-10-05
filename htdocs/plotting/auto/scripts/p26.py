import psycopg2.extras
import numpy as np
import pandas as pd
import datetime
from pyiem.network import Table as NetworkTable

PDICT = {'fall': 'Minimum Temperature after 1 July',
         'spring': 'Maximum Temperature before 1 July'}
PDICT2 = {'high': 'High Temperature',
          'low': 'Low Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents the climatology and actual
    year's progression of warmest to date or coldest to date temperature.
    The simple average is presented along with the percentile intervals."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='year', name='year', default=datetime.datetime.now().year,
             label='Year to Highlight:'),
        dict(type='select', name='half', default='fall',
             label='Option to Plot:', options=PDICT),
        dict(type='select', name='var', default='low',
             label='Variable to Plot:', options=PDICT2),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    today = datetime.date.today()
    thisyear = today.year
    year = int(fdict.get('year', thisyear))
    station = fdict.get('station', 'IA0200')
    varname = fdict.get('var', 'low')
    half = fdict.get('half', 'fall')
    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    startyear = int(nt.sts[station]['archive_begin'].year)
    data = np.ma.ones((thisyear-startyear+1, 366)) * 199
    if half == 'fall':
        cursor.execute("""SELECT extract(doy from day), year,
            """ + varname + """ from
            """+table+""" WHERE station = %s and low is not null and
            high is not null and year >= %s""", (station, startyear))
    else:
        cursor.execute("""SELECT extract(doy from day), year,
            """ + varname + """ from
            """+table+""" WHERE station = %s and high is not null and
            low is not null and year >= %s""", (station, startyear))
    for row in cursor:
        data[row[1] - startyear, row[0] - 1] = row[2]

    data.mask = np.where(data == 199, True, False)

    doys = []
    avg = []
    p25 = []
    p2p5 = []
    p75 = []
    p97p5 = []
    mins = []
    maxs = []
    dyear = []
    idx = year - startyear
    last_doy = int(today.strftime("%j"))
    if half == 'fall':
        for doy in range(181, 366):
            l = np.ma.min(data[:-1, 180:doy], 1)
            avg.append(np.ma.average(l))
            mins.append(np.ma.min(l))
            maxs.append(np.ma.max(l))
            p = np.percentile(l, [2.5, 25, 75, 97.5])
            p2p5.append(p[0])
            p25.append(p[1])
            p75.append(p[2])
            p97p5.append(p[3])
            doys.append(doy)
            if year == thisyear and doy > last_doy:
                continue
            dyear.append(np.ma.min(data[idx, 180:doy]))
    else:
        for doy in range(1, 181):
            l = np.ma.max(data[:-1, :doy], 1)
            avg.append(np.ma.average(l))
            mins.append(np.ma.min(l))
            maxs.append(np.ma.max(l))
            p = np.percentile(l, [2.5, 25, 75, 97.5])
            p2p5.append(p[0])
            p25.append(p[1])
            p75.append(p[2])
            p97p5.append(p[3])
            doys.append(doy)
            if year == thisyear and doy > last_doy:
                continue
            dyear.append(np.ma.max(data[idx, :doy]))

    # http://stackoverflow.com/questions/19736080
    d = dict(doy=pd.Series(doys), min=pd.Series(mins), max=pd.Series(maxs),
             p2p5=pd.Series(p2p5),
             p97p5=pd.Series(p97p5), p25=pd.Series(p25),
             p75=pd.Series(p75), avg=pd.Series(avg),
             thisyear=pd.Series(dyear))
    df = pd.DataFrame(d)
    (fig, ax) = plt.subplots(1, 1)

    ax.fill_between(doys, mins, maxs, color='pink', zorder=1, label='Range')
    ax.fill_between(doys, p2p5, p97p5, color='tan', zorder=2, label='95 tile')
    ax.fill_between(doys, p25, p75, color='gold', zorder=3, label='50 tile')
    a = ax.plot(doys, avg, zorder=4, color='k', lw=2, label='Average')
    ax.plot(doys[:len(dyear)], dyear, color='white', lw=3.5, zorder=5)
    b = ax.plot(doys[:len(dyear)], dyear, color='b', lw=1.5, zorder=6,
                label='%s' % (year,))
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                        'Sep', 'Oct', 'Nov', 'Dec'))
    if half == 'fall':
        ax.set_xlim(200, 366)
        ax.text(220, 32.4, r'32$^\circ$F', ha='left')
        title = "Minimum Daily %s Temperature after 1 July"
    else:
        ax.set_xlim(0, 181)
        title = "Maximum Daily %s Temperature before 1 July"
    title = title % (varname.capitalize(), )
    ax.set_ylabel(title + " $^\circ$F")
    ax.set_title("%s-%s %s %s\n%s" % (startyear,
                                      thisyear-1, station,
                                      nt.sts[station]['name'], title))
    ax.axhline(32, linestyle='--', lw=1, color='k', zorder=6)
    ax.grid(True)

    from matplotlib.patches import Rectangle
    r = Rectangle((0, 0), 1, 1, fc='pink')
    r2 = Rectangle((0, 0), 1, 1, fc='tan')
    r3 = Rectangle((0, 0), 1, 1, fc='gold')

    loc = 1 if half == 'fall' else 4
    ax.legend([r, r2, r3, a[0], b[0]], ['Range', '95$^{th}$ %tile',
                                        '50$^{th}$ %tile', 'Average',
                                        '%s' % (year,)], loc=loc)

    return fig, df
