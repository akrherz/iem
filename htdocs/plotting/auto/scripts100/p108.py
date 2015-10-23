import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents accumulated totals and departures
    of growing degree days, precipitation and stress degree days. Leap days
    are not considered for this plot."""
    today = datetime.date.today()
    if today.month < 5:
        today = today.replace(year=today.year - 1, month=10, day=1)
    sts = today.replace(month=5, day=1)

    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='date', name='sdate',
             default=sts.strftime("%Y/%m/%d"),
             label='Start Date (inclusive):', min="1893/01/01"),
        dict(type='date', name='edate',
             default=today.strftime("%Y/%m/%d"),
             label='End Date (inclusive):', min="1893/01/01"),
        dict(type="text", name="base", default="50",
             label="Growing Degree Day Base (F)"),
        dict(type="text", name="ceil", default="86",
             label="Growing Degree Day Ceiling (F)"),
        dict(type='year', name='year2', default=1893, optional=True,
             label="Compare with year (optional):"),
        dict(type='year', name='year3', default=1893, optional=True,
             label="Compare with year (optional)"),
        dict(type='year', name='year4', default=1893, optional=True,
             label="Compare with year (optional)"),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA2203')
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    sdate = datetime.datetime.strptime(fdict.get('sdate', '2015-01-01'),
                                       '%Y-%m-%d')
    edate = datetime.datetime.strptime(fdict.get('edate', '2015-02-01'),
                                       '%Y-%m-%d')
    year2 = int(fdict.get('year2', 0))
    year3 = int(fdict.get('year3', 0))
    year4 = int(fdict.get('year4', 0))
    gddbase = int(fdict.get('base', 50))
    gddceil = int(fdict.get('ceil', 86))
    glabel = "gdd%s%s" % (gddbase, gddceil)

    table = "alldata_%s" % (station[:2], )
    df = read_sql("""
    WITH climate_data as (
        SELECT sday, avg(gddxx(%s, %s, high, low)) as c"""+glabel+""",
        avg(sdd86(high, low)) as sdd86, avg(precip) as precip from """+table+"""
        WHERE station = %s GROUP by sday)

    SELECT o.sday, o.day, gddxx(%s, %s, o.high, o.low) as o"""+glabel+""",
    c.c"""+glabel+""",
    o.precip as oprecip, c.precip as cprecip,
    sdd86(o.high, o.low) as osdd86, c.sdd86 as csdd86
    from climate_data c JOIN """ + table + """ o on
    (c.sday = o.sday)
    WHERE o.station = %s and o.day >= %s and o.day <= %s and o.sday != '0229'
    ORDER by o.day ASC
    """, pgconn, params=(gddbase, gddceil, station, gddbase, gddceil, station,
                         sdate, edate),
                  index_col='sday')

    for year in [year2, year3, year4]:
        if year == 0:
            continue
        s1 = sdate.replace(year=year)
        s2 = edate.replace(year=year)
        df2 = read_sql("""SELECT sday, day,
            gddxx(%s, %s, o.high, o.low) as o"""+glabel+""",
            o.precip as oprecip, sdd86(o.high, o.low) as osdd86
            from alldata_ia o WHERE
            o.station = %s and o.day >= %s and
            o.day <= %s and sday != '0229' ORDER by o.day ASC
        """, pgconn, params=(gddbase, gddceil, station, s1, s2),
                       index_col='sday')
        df2.columns = ['%s_%s' % (v, year) for v in df2.columns]
        df = df.join(df2)

    for suffix in ['', year2, year3, year4]:
        if suffix == 0:
            continue
        s = "" if suffix == '' else '_%s' % (suffix, )
        df['cumsum_o'+glabel+s] = df["o"+glabel+s].cumsum()
        if suffix == '':
            df['cumsum_c'+glabel+s] = df["c"+glabel+s].cumsum()
        df['diff_'+glabel+s] = df["cumsum_o"+glabel+s] - df['cumsum_c'+glabel]
        df['cumsum_oprecip'+s] = df["oprecip"+s].cumsum()
        if suffix == '':
            df['cumsum_cprecip'+s] = df["cprecip"+s].cumsum()
        df['cumsum_osdd86'+s] = df["osdd86"+s].cumsum()
        if suffix == '':
            df['cumsum_csdd86'+s] = df["csdd86"+s].cumsum()

    fig = plt.figure(figsize=(9, 12))
    ax1 = fig.add_axes([0.1, 0.7, 0.8, 0.2])
    ax2 = fig.add_axes([0.1, 0.6, 0.8, 0.1], sharex=ax1, axisbg='#EEEEEE')
    ax3 = fig.add_axes([0.1, 0.35, 0.8, 0.2], sharex=ax1)
    ax4 = fig.add_axes([0.1, 0.1, 0.8, 0.2], sharex=ax1)

    ax1.set_title(("Accumulated GDD(base=%.0f,ceil=%.0f), Precip, & "
                   "SDD(base=86)\n%s %s"
                   ) % (gddbase, gddceil, station, nt.sts[station]['name']),
                  fontsize=18)
    yearlabel = sdate.year
    if sdate.year != edate.year:
        yearlabel = "%s-%s" % (sdate.year, edate.year)

    ax1.plot(df['day'], df['cumsum_o'+glabel], color='r',
             label='%s' % (yearlabel,), lw=2)
    ax1.plot(df['day'], df['cumsum_c'+glabel], color='k', label='Climatology',
             lw=2)
    ax1.set_ylabel(("GDD Base %.0f Ceil %.0f $^{\circ}\mathrm{F}$"
                    ) % (gddbase, gddceil), fontsize=16)

    ax1.text(0.5, 0.9, "%s/%s - %s/%s" % (sdate.month, sdate.day, edate.month,
                                          edate.day), transform=ax1.transAxes,
             ha='center')

    ax2.plot(df['day'], df['diff_'+glabel], color='r', linewidth=2,
             linestyle='--')
    spread = df['diff_'+glabel].abs().max() * 1.1
    ax2.set_ylim(0-spread, spread)
    ax2.text(0.02, 0.1, " Accumulated Departure ", transform=ax2.transAxes,
             bbox=dict(facecolor='white', ec='#EEEEEE'))
    ax2.yaxis.tick_right()

    ax3.plot(df['day'], df['cumsum_oprecip'], color='r', lw=2)
    ax3.plot(df['day'], df['cumsum_cprecip'], color='k', lw=2)
    ax3.set_ylabel("Precipitation [inch]", fontsize=16)

    ax4.plot(df['day'], df['cumsum_osdd86'], color='r', lw=2)
    ax4.plot(df['day'], df['cumsum_csdd86'], color='k', lw=2)
    ax4.set_ylabel("SDD Base 86 $^{\circ}\mathrm{F}$", fontsize=16)

    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax4.grid(True)

    for color, year in zip(['b', 'g', 'tan'], [year2, year3, year4]):
        if year == 0:
            continue
        label = "%s" % (year, )
        ax1.plot(df['day'], df['cumsum_o%s_%s' % (glabel, year)], label=label,
                 lw=2, c=color)
        ax2.plot(df['day'], df['diff_%s_%s' % (glabel, year)], label=label,
                 lw=2, c=color)
        ymax = max([df['diff_%s_%s' % (glabel, year)].abs().max() * 1.1,
                    ax2.get_ylim()[1]])
        ax2.set_ylim(0-ymax, ymax)
        ax3.plot(df['day'], df['cumsum_oprecip_%s' % (year, )], label=label,
                 lw=2, c=color)
        ax4.plot(df['day'], df['cumsum_osdd86_%s' % (year, )], label=label,
                 lw=2, c=color)
    if (df['day'].iat[-1] - df['day'].iat[0]).days < 32:
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    else:
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))
    ax1.legend(loc=2, prop={'size': 12})

    # Remove ticks on the top most plot
    for label in ax1.get_xticklabels():
        label.set_visible(False)

    return fig, df

if __name__ == '__main__':
    plotter(dict())
