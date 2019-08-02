"""max temp before jul 1 or min after"""
import datetime

import psycopg2.extras
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {'fall': 'Minimum Temperature after 1 July',
         'spring': 'Maximum Temperature before 1 July'}
PDICT2 = {'high': 'High Temperature',
          'low': 'Low Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['highcharts'] = True
    desc['description'] = """This plot presents the climatology and actual
    year's progression of warmest to date or coldest to date temperature.
    The simple average is presented along with the percentile intervals."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:', network='IACLIMATE'),
        dict(type='year', name='year', default=datetime.datetime.now().year,
             label='Year to Highlight:'),
        dict(type='select', name='half', default='fall',
             label='Option to Plot:', options=PDICT),
        dict(type='select', name='var', default='low',
             label='Variable to Plot:', options=PDICT2),
        dict(type='int', name='t', label='Highlight Temperature',
             default=32),
    ]
    return desc


def get_context(fdict):
    """ Get the raw infromations we need"""
    pgconn = get_dbconn('coop')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    today = datetime.date.today()
    thisyear = today.year
    ctx = get_autoplot_context(fdict, get_description())
    year = ctx['year']
    station = ctx['station']
    varname = ctx['var']
    half = ctx['half']
    table = "alldata_%s" % (station[:2],)

    ab = ctx['_nt'].sts[station]['archive_begin']
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    startyear = int(ab.year)
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
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found.")
    for row in cursor:
        data[int(row[1] - startyear), int(row[0] - 1)] = row[2]

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
            low = np.ma.min(data[:-1, 180:doy], 1)
            avg.append(np.ma.average(low))
            mins.append(np.ma.min(low))
            maxs.append(np.ma.max(low))
            p = np.percentile(low, [2.5, 25, 75, 97.5])
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
            low = np.ma.max(data[:-1, :doy], 1)
            avg.append(np.ma.average(low))
            mins.append(np.ma.min(low))
            maxs.append(np.ma.max(low))
            p = np.percentile(low, [2.5, 25, 75, 97.5])
            p2p5.append(p[0])
            p25.append(p[1])
            p75.append(p[2])
            p97p5.append(p[3])
            doys.append(doy)
            if year == thisyear and doy > last_doy:
                continue
            dyear.append(np.ma.max(data[idx, :doy]))

    # http://stackoverflow.com/questions/19736080
    d = dict(doy=pd.Series(doys), mins=pd.Series(mins), maxs=pd.Series(maxs),
             p2p5=pd.Series(p2p5),
             p97p5=pd.Series(p97p5), p25=pd.Series(p25),
             p75=pd.Series(p75), avg=pd.Series(avg),
             thisyear=pd.Series(dyear))
    df = pd.DataFrame(d)
    sts = datetime.date(2000, 1, 1) + datetime.timedelta(days=doys[0]-1)
    df['dates'] = pd.date_range(sts, periods=len(doys))
    df.set_index('doy', inplace=True)
    ctx['df'] = df
    ctx['year'] = year
    ctx['half'] = half
    if ctx['half'] == 'fall':
        title = "Minimum Daily %s Temperature after 1 July"
    else:
        title = "Maximum Daily %s Temperature before 1 July"
    title = title % (varname.capitalize(), )
    ctx['ylabel'] = title
    ctx['title'] = "%s-%s %s %s\n%s" % (startyear,
                                        thisyear-1, station,
                                        ctx['_nt'].sts[station]['name'], title)
    return ctx


def highcharts(fdict):
    """ Do highcharts """
    ctx = get_context(fdict)

    rng = ctx['df'][['dates', 'mins', 'maxs']].to_json(orient='values')
    p95 = ctx['df'][['dates', 'p2p5', 'p97p5']].to_json(orient='values')
    p50 = ctx['df'][['dates', 'p25', 'p75']].to_json(orient='values')
    mean = ctx['df'][['dates', 'avg']].to_json(orient='values')
    thisyear = ctx['df'][['dates', 'thisyear']].to_json(orient='values')
    return """
$("#ap_container").highcharts({
    title: {text: '""" + ctx['title'].replace("\n", " ") + """'},
    tooltip: {shared: true,
        xDateFormat: '%B %d'},
    xAxis: {type: 'datetime',
        dateTimeLabelFormats: {
            day: '%b %e',
            week: '%b %e',
            month: '%b %e'}},
    yAxis: {title: {text: '"""+ctx['ylabel']+"""'}},
    series: [{
        name: 'Range',
        type: 'arearange',
        color: 'pink',
        tooltip: {valueDecimals: 0},
        data: """+rng+"""
    },{
        name: '95th',
        type: 'arearange',
        color: 'tan',
        tooltip: {valueDecimals: 2},
        data: """+p95+"""
    },{
        name: '50th',
        type: 'arearange',
        color: 'gold',
        tooltip: {valueDecimals: 2},
        data: """+p50+"""
    },{
        name: 'Average',
        type: 'line',
        color: 'black',
        tooltip: {valueDecimals: 2},
        data: """+mean+"""
    },{
        name: '"""+str(ctx['year'])+"""',
        type: 'line',
        color: 'blue',
        tooltip: {valueDecimals: 0},
        shadow: {'color': 'white'},
        data: """+thisyear+"""
    }]
});
    """


def plotter(fdict):
    """ Go """
    ctx = get_context(fdict)
    df = ctx['df']

    (fig, ax) = plt.subplots(1, 1)
    doys = df.index.values
    ax.fill_between(doys, df['mins'], df['maxs'], color='pink',
                    zorder=1, label='Range')
    ax.fill_between(doys, df['p2p5'], df['p97p5'],
                    color='tan', zorder=2, label='95 tile')
    ax.fill_between(doys, df['p25'], df['p75'],
                    color='gold', zorder=3, label='50 tile')
    a = ax.plot(doys, df['avg'], zorder=4, color='k', lw=2,
                label='Average')
    series = df['thisyear'].dropna()
    ax.plot(series.index.values, series.values, color='white',
            lw=3.5, zorder=5)
    b = ax.plot(series.index.values, series.values, color='b', lw=1.5,
                zorder=6, label='%s' % (ctx['year'],))
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                        'Sep', 'Oct', 'Nov', 'Dec'))
    if ctx['half'] == 'fall':
        ax.set_xlim(200, 366)
    else:
        ax.set_xlim(0, 181)
    ax.set_ylabel(r"%s $^\circ$F" % (ctx['ylabel'], ))
    ax.set_title(ctx['title'])
    ax.axhline(ctx['t'], linestyle='--', lw=1, color='k', zorder=6)
    ax.text(ax.get_xlim()[1], ctx['t'], r"%.0f$^\circ$F" % (ctx['t'], ),
            va='center')
    ax.grid(True)

    r = Rectangle((0, 0), 1, 1, fc='pink')
    r2 = Rectangle((0, 0), 1, 1, fc='tan')
    r3 = Rectangle((0, 0), 1, 1, fc='gold')

    loc = 1 if ctx['half'] == 'fall' else 4
    ax.legend([r, r2, r3, a[0], b[0]], ['Range', '95$^{th}$ %tile',
                                        '50$^{th}$ %tile', 'Average',
                                        '%s' % (ctx['year'],)], loc=loc)

    return fig, df


if __name__ == '__main__':
    highcharts(dict())
