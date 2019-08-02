"""Special Days each year"""
import datetime
import calendar
from collections import OrderedDict

from dateutil.easter import easter as get_easter
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict([
        ('easter', 'Easter (Western Church Dates)'),
        ('labor', 'Labor Day'),
        ('memorial', 'Memorial Day'),
        ('mother', "Mothers Day"),
        ('exact', 'Same Date each Year'),
        ('thanksgiving', 'Thanksgiving'),
        ])
PDICT2 = OrderedDict([
        ('high', 'High Temperature [F]'),
        ('low', 'Low Temperature [F]'),
        ('precip', 'Precipitation [inch]'),
        ])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['highcharts'] = True
    desc['cache'] = 86400
    desc['description'] = """This plot presents a daily observation for a site
    and year on a given date / holiday date each year.  A large caveat to this
    chart is that much of the long term daily climate data is for a 24 hour
    period ending at around 7 AM.  This chart will also not plot for dates
    prior to the holiday's inception.
    """
    desc['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             network='IACLIMATE', label='Select Station:'),
        dict(type='select', name='date', default='memorial', options=PDICT,
             label='Which date/holiday to plot?'),
        dict(type='date', name='thedate', default='2000/01/01',
             min='2000/01/01', max='2000/12/31',
             label='Same date each year to plot (when selected above):'),
        dict(type='select', name='var', default='high',
             label='Which variable to plot?', options=PDICT2)
    ]
    return desc


def mothers_day():
    """Mother's Day"""
    days = []
    for year in range(1914, datetime.date.today().year + 1):
        may1 = datetime.date(year, 5, 1)
        days.append(datetime.date(year, 5, (14 - may1.weekday())))
    return days


def easter():
    """Compute easter"""
    return [get_easter(year) for year in range(1893,
                                               datetime.date.today().year + 1)]


def thanksgiving():
    """Thanksgiving please"""
    days = []
    # monday is 0
    offsets = [3, 2, 1, 0, 6, 5, 4]
    for year in range(1893, datetime.date.today().year + 1):
        nov1 = datetime.datetime(year, 11, 1)
        r1 = nov1 + datetime.timedelta(days=offsets[nov1.weekday()])
        days.append(r1 + datetime.timedelta(days=21))
    return days


def labor_days():
    """Labor Day Please"""
    days = []
    for year in range(1893, datetime.date.today().year + 1):
        mycal = calendar.Calendar(0)
        cal = mycal.monthdatescalendar(year, 9)
        if cal[0][0].month == 9:
            days.append(cal[0][0])
        else:
            days.append(cal[1][0])
    return days


def memorial_days():
    """Memorial Day Please"""
    days = []
    for year in range(1971, datetime.date.today().year + 1):
        mycal = calendar.Calendar(0)
        cal = mycal.monthdatescalendar(year, 5)
        if cal[-1][0].month == 5:
            days.append(cal[-1][0])
        else:
            days.append(cal[-2][0])
    return days


def get_context(fdict):
    """Do the dirty work"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    ctx['varname'] = ctx['var']
    thedate = ctx['thedate']
    date = ctx['date']

    pgconn = get_dbconn('coop')

    table = "alldata_%s" % (station[:2], )
    if date == 'exact':
        ctx['df'] = read_sql("""
            SELECT year, high, day, precip from """ + table + """
            WHERE station = %s
            and sday = %s ORDER by year ASC
        """, pgconn, params=(station, thedate.strftime("%m%d")),
                             index_col='year')
        ctx['subtitle'] = thedate.strftime("%B %-d")
    else:
        if date == 'memorial':
            days = memorial_days()
        elif date == 'thanksgiving':
            days = thanksgiving()
        elif date == 'easter':
            days = easter()
        elif date == 'mother':
            days = mothers_day()
        else:
            days = labor_days()

        ctx['df'] = read_sql("""
        SELECT year, high, day, precip from """ + table + """
        WHERE station = %s
        and day in %s ORDER by year ASC
        """, pgconn, params=(station, tuple(days)),
                             index_col='year')
        ctx['subtitle'] = PDICT[date]
    if ctx['df'].empty:
        raise NoDataFound("No Data Found.")
    ctx['title'] = (
        "%s [%s] Daily %s"
        ) % (ctx['_nt'].sts[ctx['station']]['name'], ctx['station'],
             PDICT2[ctx['varname']])
    return ctx


def highcharts(fdict):
    """Generate javascript (Highcharts) variant"""
    ctx = get_context(fdict)
    ctx['df'].reset_index(inplace=True)
    v2 = ctx['df'][['year', ctx['varname']]].to_json(orient='values')
    avgval = ctx['df'][ctx['varname']].mean()
    avgvallbl = "%.2f" % (avgval,)
    series = """{
        name: '""" + ctx['varname'] + """',
        data: """ + v2 + """,
        color: '#0000ff'
    }
    """

    return """
    $("#ap_container").highcharts({
        chart: {
            type: 'column',
            zoomType: 'x'
        },
        yAxis: {
            title: {text: '""" + PDICT2[ctx['varname']] + """'},
            plotLines: [{
                value: """ + str(avgval) + """,
                color: 'green',
                dashStyle: 'shortdash',
                width: 2,
                zIndex: 5,
                label: {
                    text: 'Average """ + avgvallbl + """'
                }
            }]
        },
        title: {text: '""" + ctx['title'] + """'},
        subtitle: {text: 'On """ + ctx['subtitle'] + """'},
        series: [""" + series + """]
    });
    """


def plotter(fdict):
    """ Go """
    ctx = get_context(fdict)

    (fig, ax) = plt.subplots(1, 1)

    ax.bar(ctx['df'].index.values, ctx['df'][ctx['varname']],
           fc='r', ec='r', align='center')
    mean = ctx['df'][ctx['varname']].mean()
    ax.axhline(mean)
    ax.set_title("%s\non %s" % (ctx['title'], ctx['subtitle']))
    ax.text(ctx['df'].index.values[-1] + 1, mean, '%.2f' % (mean,), ha='left',
            va='center')
    ax.grid(True)
    ax.set_xlim(ctx['df'].index.values.min() - 1,
                ctx['df'].index.values.max() + 1)
    ax.set_ylabel(PDICT2[ctx['varname']])
    if ctx['varname'] != 'precip':
        ax.set_ylim(ctx['df'][ctx['varname']].min() - 5,
                    ctx['df'][ctx['varname']].max() + 5)
    return fig, ctx['df']


if __name__ == '__main__':
    plotter(dict(date='easter'))
