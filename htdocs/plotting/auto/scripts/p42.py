import psycopg2.extras
import datetime
import pytz
import pandas as pd
from pyiem.network import Table as NetworkTable

PDICT = {'above': 'At or Above Threshold...',
         'below': 'Below Threshold...'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 86400
    d['data'] = True
    d['description'] = """ Based on hourly METAR reports of temperature, this
    plot displays the longest periods above or below a given temperature
    threshold.  There are plenty of caveats to this plot, including missing
    data periods that are ignored and data during the 1960s that only has
    reports every three hours.  This plot also limits the number of lines
    drawn to 10, so if you hit the limit, please change the thresholds.
    """
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:'),
        dict(type='month', name='month', label='Select Month:', default=12),
        dict(type='select', name='dir', default='above',
             label='Threshold Direction:', options=PDICT),
        dict(type='text', name='threshold', default=50,
             label='Temperature (F) Threshold:'),
        dict(type='text', name='hours', default=36,
             label='Minimum Period to Plot (Hours):')
    ]
    return d


def plot(ax, interval, valid, tmpf, year, lines):
    """ Our plotting function """
    if len(valid) == 0:
        return lines
    if (valid[-1] - valid[0]) > interval:
        if len(lines) == 10:
            ax.text(0.5, 0.9, "ERROR: Limit of 10 lines reached",
                    transform=ax.transAxes)
            return lines
        if len(lines) > 10:
            return lines
        delta = ((valid[-1] - valid[0]).days * 86400. +
                 (valid[-1] - valid[0]).seconds)
        i = tmpf.index(min(tmpf))
        mylbl = "%s\n%.1fd" % (year, delta / 86400.)
        lines.append(ax.plot(valid, tmpf, lw=2,
                             label=mylbl.replace("\n", " "))[0])
        lines[-1].hours = round((valid[-1] - valid[0]).seconds / 3600., 2)
        lines[-1].days = (valid[-1] - valid[0]).days
        lines[-1].year = year
        lines[-1].mylbl = mylbl
        ax.text(valid[i], tmpf[i], mylbl,
                ha='center', va='center',
                bbox=dict(color=lines[-1].get_color()),
                color='white')
    return lines


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    threshold = int(fdict.get('threshold', 32))
    month = int(fdict.get('month', 12))
    mydir = fdict.get('dir', 'below')
    hours = int(fdict.get('hours', 48))

    nt = NetworkTable(network)

    cursor.execute("""
      SELECT valid, round(tmpf::numeric,0)  from alldata where station = %s
      and tmpf is not null and extract(month from valid) = %s
      ORDER by valid ASC
      """, (station, month))

    (fig, ax) = plt.subplots(1, 1)
    interval = datetime.timedelta(hours=hours)

    valid = []
    tmpf = []
    year = 0
    lines = []
    for row in cursor:
        if year != row[0].year:
            year = row[0].year
            lines = plot(ax, interval, valid, tmpf, year, lines)
            valid = []
            tmpf = []
        if ((mydir == 'above' and row[1] >= threshold) or
                (mydir == 'below' and row[1] < threshold)):
            valid.append(row[0].replace(year=2000))
            tmpf.append(row[1])
        if ((mydir == 'above' and row[1] < threshold) or
                (mydir == 'below' and row[1] >= threshold)):
            valid.append(row[0].replace(year=2000))
            tmpf.append(row[1])
            lines = plot(ax, interval, valid, tmpf, year, lines)
            valid = []
            tmpf = []

    lines = plot(ax, interval, valid, tmpf, year, lines)
    rows = []
    for line in lines:
        xdata = line.get_xdata()
        rows.append(dict(start=xdata[0].replace(year=line.year),
                         end=xdata[-1].replace(year=line.year),
                         hours=line.hours, days=line.days))
    df = pd.DataFrame(rows)

    sts = datetime.datetime(2000, month, 1)
    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)
    ax.set_xlim(sts, ets)
    ax.xaxis.set_major_locator(
        mdates.DayLocator(interval=2,
                          tz=pytz.timezone(nt.sts[station]['tzname'])))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d'))
    ax.grid(True)
    ax.set_ylabel("Temperature $^\circ$F")
    ax.set_xlabel("Day of %s (%s)" % (sts.strftime("%B"),
                                      nt.sts[station]['tzname']))
    ax.set_title(("%s-%s [%s] %s\n%s :: %.1f+ Day Streaks %s %s$^\circ$F"
                  ) % (nt.sts[station]['archive_begin'].year,
                       datetime.datetime.now().year, station,
                       nt.sts[station]['name'], sts.strftime("%B"),
                       hours / 24.0, mydir, threshold))
    # ax.axhline(32, linestyle='-.', linewidth=2, color='k')
    # ax.set_ylim(bottom=43)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.15,
                     box.width, box.height * 0.85])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
              fancybox=True, shadow=True, ncol=5, fontsize=12,
              columnspacing=1)
    return fig, df
