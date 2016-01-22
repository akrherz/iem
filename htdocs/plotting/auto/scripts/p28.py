import psycopg2.extras
import numpy as np
import datetime
import pandas as pd
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    today = datetime.date.today()
    d['data'] = True
    d['highcharts'] = True
    d['description'] = """This plot presents three metrics for to date
    precipitation accumulation over a given number of trailing days.  The
    lines represent the actual and maximum accumulations for the period.
    The blue bars represent the rank with 1 being the wettest on record."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='date', name='date', default=today.strftime("%Y/%m/%d"),
             label='To Date:',
             min="1894/01/01"),  # Comes back to python as yyyy-mm-dd

    ]
    return d


def get_ctx(fdict):
    """Get the plotting context """
    ctx = {}
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    date = datetime.datetime.strptime(fdict.get('date', '2014-10-15'),
                                      '%Y-%m-%d')

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    cursor.execute("""
    SELECT year,  extract(doy from day) as doy, precip
    from """+table+""" where station = %s and precip is not null
    """, (station,))

    baseyear = nt.sts[station]['archive_begin'].year - 1
    years = (datetime.datetime.now().year - baseyear) + 1

    data = np.zeros((years, 367*2))
    # 1892 1893
    # 1893 1894
    # 1894 1895

    for row in cursor:
        # left hand
        data[int(row['year'] - baseyear), int(row['doy'])] = row['precip']
        # right hand
        data[int(row['year'] - baseyear - 1),
             int(row['doy']) + 366] = row['precip']

    _temp = date.replace(year=2000)
    _doy = int(_temp.strftime("%j"))
    xticks = []
    xticklabels = []
    for i in range(-366, 0):
        ts = _temp + datetime.timedelta(days=i)
        if ts.day == 1:
            xticks.append(i)
            xticklabels.append(ts.strftime("%b"))
    ranks = []
    totals = []
    maxes = []
    avgs = []
    myyear = date.year - baseyear - 1
    for days in range(1, 366):
        idx0 = _doy + 366 - days
        idx1 = _doy + 366
        sums = np.sum(data[:, idx0:idx1], 1)
        thisyear = sums[myyear]
        sums = np.sort(sums)
        a = np.digitize([thisyear, ], sums)
        rank = years - a[0] + 1
        ranks.append(rank)
        totals.append(thisyear)
        maxes.append(sums[-1])
        avgs.append(np.nanmean(sums))

    ctx['sdate'] = date.date() - datetime.timedelta(days=360)
    ctx['title'] = "%s %s" % (station,
                              nt.sts[station]['name'])
    ctx['subtitle'] = ("Trailing Days Precipitation Rank [%s-%s] to %s"
                       ) % (baseyear+2,
                            datetime.datetime.now().year,
                            date.strftime("%-d %b %Y"))

    ctx['ranks'] = ranks
    ctx['totals'] = totals
    ctx['maxes'] = maxes
    ctx['avgs'] = avgs
    ctx['xticks'] = xticks
    ctx['xticklabels'] = xticklabels
    ctx['station'] = station
    return ctx


def highcharts(fdict):
    """ Go """
    ctx = get_ctx(fdict)
    dstart = "Date.UTC(%s, %s, %s)" % (ctx['sdate'].year,
                                       ctx['sdate'].month - 1,
                                       ctx['sdate'].day)
    return """
$("#ap_container").highcharts({
    title: {text: '""" + ctx['title'] + """'},
    subtitle: {text: '""" + ctx['subtitle'] + """'},
    chart: {zoomType: 'x'},
    yAxis: [{
            min: 0,
            title: {
                text: 'Precipitation [inch]'
            }
        }, {
            min: 0,
            title: {
                text: 'Rank [1 is wettest]'
            },
            opposite: true
    }],
    tooltip: {
        shared: true,
        xDateFormat: '%Y-%m-%d'
    },
    series : [{
        name: 'Rank',
        pointStart: """ + dstart + """,
        pointInterval: 24 * 3600 * 1000, // one day
        zIndex: 5,
        shadow: true,
        data: """ + str(ctx['ranks'][::-1]) + """,
        yAxis: 1
    },{
        name: 'This Period',
        tooltip: {valueDecimals: 2},
        pointStart: """ + dstart + """,
        pointInterval: 24 * 3600 * 1000, // one day
        zIndex: 3,
        data: """ + str(ctx['totals'][::-1]) + """
    },{
        name: 'Average',
        tooltip: {valueDecimals: 2},
        pointStart: """ + dstart + """,
        pointInterval: 24 * 3600 * 1000, // one day
        zIndex: 4,
        data: """ + str(ctx['avgs'][::-1]) + """
    }, {
        name: 'Maximum',
        zIndex: 2,
        tooltip: {valueDecimals: 2},
        pointStart: """ + dstart + """,
        pointInterval: 24 * 3600 * 1000, // one day
        data: """ + str(ctx['maxes'][::-1]) + """
    }],
    xAxis: {
        type: 'datetime'
    }

});

    """


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ctx = get_ctx(fdict)

    (fig, ax) = plt.subplots(1, 1)
    y2 = ax.twinx()

    y2.bar(np.arange(-365, 0), ctx['ranks'][::-1], fc='b', ec='b')
    ax.grid(True)
    ax.set_xticks(ctx['xticks'])
    ax.set_xticklabels(ctx['xticklabels'])
    ax.set_title(("%s\n%s") % (ctx['title'], ctx['subtitle']))
    y2.set_ylabel("Rank [1=wettest] (bars)", color='b')
    ax.set_xlim(-367, 0.5)

    ax.plot(np.arange(-365, 0), ctx['totals'][::-1], color='r', lw=2,
            label='This Period')
    ax.plot(np.arange(-365, 0), ctx['maxes'][::-1], color='g', lw=2,
            label='Maximum')
    ax.set_ylabel("Precipitation [inch]")

    ax.legend()
    df = pd.DataFrame(dict(day=np.arange(-365, 0),
                           maxaccum=ctx['maxes'][::-1],
                           accum=ctx['totals'][::-1],
                           rank=ctx['ranks'][::-1]))

    return fig, df

if __name__ == '__main__':
    highcharts(dict())
