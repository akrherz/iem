"""monthly comparisons"""
import datetime
import calendar

import numpy as np
from scipy import stats
from pyiem import network, util
from pandas.io.sql import read_sql
import pandas as pd

PDICT = {'total_precip': 'Total Precipitation',
         'avg_temp': 'Average Temperature',
         'max_high': 'Maximum High Temperature',
         'days_high_aoa': 'Days with High At or Above',
         'gdd50': 'Growing Degree Days (base 50)'}

UNITS = {'total_precip': 'inch',
         'avg_temp': 'F',
         'max_high': 'F',
         'days_high_aoa': 'days',
         'gdd50': 'F'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=60)
    desc['description'] = """This app allows the arbitrary comparison of months
    against other months.  When the period of months wraps around a new
    year, the app attempts to keep this situation straight with Dec and Jan
    following each other.  The periods are combined together based on the
    year of the beginning month of each period. If there is a metric you
    wished to see added to this analysis, please
    <a href="/info/contacts.php">let us know</a>!"""
    desc['arguments'] = [
        dict(type='station', name='station', default='IA0000',
             label='Select Station', network='IACLIMATE'),
        dict(type='int', name='threshold', default='93',
             label='Daily Temperature Threshold (when appropriate)'),
        dict(type='month', name='month1', default=yesterday.month,
             label='Month 1 for Comparison'),
        dict(type='int', name='num1', default=2,
             label='Number of Additional Months for Comparison 1'),
        dict(type='select', options=PDICT, default='total_precip', name='var1',
             label='Comparison 1 Variable'),
        dict(type='month', name='month2', default=yesterday.month,
             label='Month 2 for Comparison'),
        dict(type='int', name='num2', default=2,
             label='Number of Additional Months for Comparison 2'),
        dict(type='select', options=PDICT, default='avg_temp', name='var2',
             label='Comparison 2 Variable'),
    ]
    return desc


def compute_months_and_offsets(start, count):
    """ Figure out an array of values """
    months = [start]
    offsets = [0]
    for i in range(1, count):
        nextval = start + i
        if nextval > 12:
            nextval -= 12
            offsets.append(1)
        else:
            offsets.append(0)
        months.append(nextval)

    return months, offsets


def combine(df, months, offsets):
    # To allow for periods that cross years! We create a second dataframe with
    # the year shifted back one!
    df_shift = df.copy()
    df_shift.index = df_shift.index - 1

    # We create the xaxis dataset
    xdf = df[df['month'] == months[0]].copy()
    for i, month in enumerate(months):
        if i == 0:
            continue
        if offsets[i] == 1:
            thisdf = df_shift[df_shift['month'] == month]
        else:
            thisdf = df[df['month'] == month]
        # Do our combinations, we divide out later when necessary
        for v in ['avg_temp', 'total_precip', 'gdd50', 'days_high_aoa']:
            xdf[v] = xdf[v] + thisdf[v]
        tmpdf = pd.DataFrame({'a': xdf['max_high'], 'b': thisdf['max_high']})
        xdf['max_high'] = tmpdf.max(axis=1)
    if len(months) > 1:
        xdf['avg_temp'] = xdf['avg_temp'] / float(len(months))

    return xdf


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = util.get_dbconn('coop')

    today = datetime.date.today()
    ctx = util.get_autoplot_context(fdict, get_description())
    station = ctx['station']
    threshold = ctx['threshold']
    month1 = ctx['month1']
    varname1 = ctx['var1']
    num1 = min([12, ctx['num1']])
    month2 = ctx['month2']
    varname2 = ctx['var2']
    num2 = min([12, ctx['num2']])
    months1, offsets1 = compute_months_and_offsets(month1, num1)
    months2, offsets2 = compute_months_and_offsets(month2, num2)
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))
    # Compute the monthly totals
    df = read_sql("""
    SELECT year, month, avg((high+low)/2.) as avg_temp,
    sum(precip) as total_precip, max(high) as max_high,
    sum(case when high >= %s then 1 else 0 end) as days_high_aoa,
    sum(gddxx(50, 86, high, low)) as gdd50
    from """+table+"""
    WHERE station = %s and day < %s GROUP by year, month
    """, pgconn, params=(threshold, station, today.replace(day=1)),
                  index_col='year')

    xdf = combine(df, months1, offsets1)
    ydf = combine(df, months2, offsets2)

    resdf = pd.DataFrame({"%s_1" % (varname1, ): xdf[varname1],
                          "%s_2" % (varname2, ): ydf[varname2]})
    resdf.dropna(inplace=True)
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    ax.scatter(resdf[varname1+"_1"], resdf[varname2+"_2"], marker='s',
               facecolor='b', edgecolor='b', label=None, zorder=3)
    ax.set_title(("%s-%s %s [%s]\n"
                  "Comparison of Monthly Periods, Quadrant Frequency Labelled"
                  ) % (resdf.index.min(), resdf.index.max(),
                       nt.sts[station]['name'], station))
    ax.grid(True)

    h_slope, intercept, r_value, _, _ = stats.linregress(resdf[varname1+"_1"],
                                                         resdf[varname2+"_2"])
    y = h_slope * np.arange(resdf[varname1+"_1"].min(),
                            resdf[varname1+"_1"].max()) + intercept
    ax.plot(np.arange(resdf[varname1+"_1"].min(),
                      resdf[varname1+"_1"].max()), y, lw=2, color='r',
            label="Slope=%.2f R$^2$=%.2f" % (h_slope, r_value ** 2))
    ax.legend(fontsize=10)
    xmonths = ", ".join([calendar.month_abbr[x] for x in months1])
    ymonths = ", ".join([calendar.month_abbr[x] for x in months2])
    t1 = "" if varname1 not in ['days_high_aoa', ] else " %.0f" % (threshold,)
    t2 = "" if varname2 not in ['days_high_aoa', ] else " %.0f" % (threshold,)
    x = resdf["%s_1" % (varname1, )].mean()
    y = resdf["%s_2" % (varname2, )].mean()
    ax.set_xlabel("%s\n%s%s [%s], Avg: %.1f" % (xmonths, PDICT[varname1], t1,
                                                UNITS[varname1], x),
                  fontsize=12)
    ax.set_ylabel("%s\n%s%s [%s], Avg: %.1f" % (ymonths, PDICT[varname2], t2,
                                                UNITS[varname2], y),
                  fontsize=12)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.05,
                     box.width, box.height * 0.95])
    ax.axhline(y, linestyle='--', color='g')
    ax.axvline(x, linestyle='--', color='g')
    ur = len(resdf[(resdf["%s_1" % (varname1, )] >= x) &
                   (resdf["%s_2" % (varname2, )] >= y)].index)
    ax.text(0.95, 0.75, "%s (%.1f%%)" % (ur,
                                         ur / float(len(resdf.index)) * 100.),
            color='tan', fontsize=24, transform=ax.transAxes, ha='right',
            zorder=2)
    lr = len(resdf[(resdf["%s_1" % (varname1, )] >= x) &
                   (resdf["%s_2" % (varname2, )] < y)].index)
    ax.text(0.95, 0.25, "%s (%.1f%%)" % (lr,
                                         lr / float(len(resdf.index)) * 100.),
            color='tan', fontsize=24, transform=ax.transAxes, ha='right',
            zorder=2)
    ll = len(resdf[(resdf["%s_1" % (varname1, )] < x) &
                   (resdf["%s_2" % (varname2, )] < y)].index)
    ax.text(0.05, 0.25, "%s (%.1f%%)" % (ll,
                                         ll / float(len(resdf.index)) * 100.),
            color='tan', fontsize=24, transform=ax.transAxes, ha='left',
            zorder=2)
    ul = len(resdf[(resdf["%s_1" % (varname1, )] < x) &
                   (resdf["%s_2" % (varname2, )] >= y)].index)
    ax.text(0.05, 0.75, "%s (%.1f%%)" % (ul,
                                         ul / float(len(resdf.index)) * 100.),
            color='tan', fontsize=24, transform=ax.transAxes, ha='left',
            zorder=2)
    return fig, resdf


if __name__ == '__main__':
    plotter(dict())
