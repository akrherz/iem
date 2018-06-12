"""Ob timeseries"""
import datetime

import psycopg2.extras
import pytz
import matplotlib.dates as mdates
import pyiem.datatypes as dt
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context, get_dbconn


def date_ticker(ax, mytz):
    """Timestamp formatter"""
    (xmin, xmax) = ax.get_xlim()
    xmin = mdates.num2date(xmin)
    xmax = mdates.num2date(xmax)
    xmin = xmin.replace(minute=0)
    xmax = (xmax + datetime.timedelta(minutes=59)).replace(minute=0)
    now = xmin
    xticks = []
    xticklabels = []
    while now <= xmax:
        lts = now.astimezone(mytz)
        if lts.hour % 6 == 0:
            fmt = "%-I %p\n%-d %b" if lts.hour == 0 else "%-I %p"
            xticks.append(now)
            xticklabels.append(lts.strftime(fmt))
        if len(xticks) > 100:
            break
        now += datetime.timedelta(hours=1)

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['cache'] = 360
    desc['description'] = """This plot presents a recent time series of
    observations.  Please note the colors and axes labels used to denote
    which variable is which in the combination plots."""
    desc['arguments'] = [
        dict(type='sid', label='Select IEM Tracked Station',
             name='station', default='AMW', network='IA_ASOS'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = get_dbconn('iem')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    network = ctx['network']

    nt = NetworkTable(network)
    if not nt.sts:
        raise ValueError(("Network Identifier %s is unknown to IEM"
                          ) % (network,))
    if station not in nt.sts:
        raise ValueError(("Station %s does not exist in network %s"
                          ) % (station, network))

    cursor.execute("""
        SELECT *, valid at time zone 'UTC' as utc_valid
        from current_log c JOIN stations t ON (t.iemid = c.iemid)
        WHERE t.network = %s and t.id = %s ORDER by valid ASC
      """, (network, station))

    tmpf = {'v': [], 'd': []}
    dwpf = {'v': [], 'd': []}
    vsby = {'v': [], 'd': []}
    ceil = {'v': [], 'd': []}
    smph = {'v': [], 'd': []}
    drct = {'v': [], 'd': []}
    for row in cursor:
        v = row['utc_valid'].replace(tzinfo=pytz.utc)
        t = row['tmpf']
        d = row['dwpf']
        v1 = row['vsby']
        s = row['sknt']
        d1 = row['drct']
        if d1 is not None and d1 >= 0 and d1 <= 360:
            drct['v'].append(v)
            drct['d'].append(d1)
        if s is not None and s >= 0 and s < 200:
            smph['v'].append(v)
            smph['d'].append(dt.speed(s, 'KT').value('MPH'))
        if t is not None and t >= -90 and t < 190:
            tmpf['v'].append(v)
            tmpf['d'].append(t)
        if d is not None and d >= -90 and d < 190:
            dwpf['v'].append(v)
            dwpf['d'].append(d)
        if v1 is not None and v1 >= 0 and v1 < 30:
            vsby['v'].append(v)
            vsby['d'].append(v1)
        c = [row['skyc1'], row['skyc2'], row['skyc3'], row['skyc4']]
        if 'OVC' in c:
            pos = c.index('OVC')
            ceil['v'].append(v)
            larr = [row['skyl1'], row['skyl2'], row['skyl3'], row['skyl4']]
            ceil['d'].append(larr[pos] / 1000.)

    (fig, ax) = plt.subplots(3, 1, figsize=(9, 9), sharex=True)

    # ____________PLOT 1___________________________
    if len(tmpf['v']) > 1:
        ax[0].plot(tmpf['v'], tmpf['d'], label='Air Temp', lw=2, color='r',
                   zorder=2)
    if len(dwpf['v']) > 1:
        ax[0].plot(dwpf['v'], dwpf['d'], label='Dew Point', lw=2, color='g',
                   zorder=1)

    ax[0].legend(loc=3, ncol=2, fontsize=10)
    ax[0].set_title("[%s] %s\nRecent Time Series" % (
        station, nt.sts[station]['name']))
    ax[0].grid(True)
    ax[0].set_ylabel("Temperature [F]")
    ax[0].set_ylim(bottom=(min(dwpf['d']) - 10))
    plt.setp(ax[0].get_xticklabels(), visible=True)

    # _____________PLOT 2____________________________
    if len(smph['v']) > 1:
        ax[1].plot(smph['v'], smph['d'], color='b')
        ax[1].set_ylabel("Wind Speed [MPH]", color='b')
        ax[1].set_ylim(bottom=0)
    if len(drct['v']) > 1:
        ax3 = ax[1].twinx()
        ax3.set_ylabel("Wind Direction", color='g')
        ax3.set_ylim(0, 360)
        ax3.set_yticks([0, 90, 180, 270, 360])
        ax3.set_yticklabels(['N', 'E', 'S', 'W', 'N'])
        ax3.scatter(drct['v'], drct['d'], s=40, color='g', marker='+')
    ax[1].grid(True)

    #  _____________PLOT 3___________________________
    mytz = pytz.timezone(nt.sts[station]['tzname'])
    ax[2].grid(True)
    ax[2].set_ylabel("Visibility [miles]", color='b')
    if len(ceil['v']) > 1:
        ax2 = ax[2].twinx()
        ax2.scatter(ceil['v'], ceil['d'], label='Visibility', marker='o',
                    s=40, color='g')
        ax2.set_ylabel("Overcast Ceiling [k ft]", color='g')
        ax2.set_ylim(bottom=0)
    if len(vsby['v']) > 1:
        ax[2].scatter(vsby['v'], vsby['d'], label='Visibility', marker='*',
                      s=40, color='b')
        ax[2].set_ylim(0, 14)
    date_ticker(ax[2], mytz)
    ax[2].set_xlabel("Plot Time Zone: %s" % (nt.sts[station]['tzname'],))

    return fig


if __name__ == '__main__':
    plotter(dict())
