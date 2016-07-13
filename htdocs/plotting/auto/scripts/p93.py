import psycopg2.extras
from pyiem.network import Table as NetworkTable
import numpy as np
import pandas as pd
import datetime
from pyiem.datatypes import temperature
import pyiem.meteorology as pymet
from pyiem.util import get_autoplot_context

PDICT = {'yes': 'Yes, Include only Year to Date period each year',
         'no': 'No, Include all available data for each year'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['desciption'] = """Caution: This plot takes a bit of time to
    generate. This plot displays a histogram of hourly heat index
    values."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:'),
        dict(type='year', minvalue=1973, default=datetime.date.today().year,
             name='year', label='Year to Highlight'),
        dict(type='select', options=PDICT, name='ytd', default='no',
             label='Include Only Year to Date Data?'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']
    highlightyear = ctx['year']
    ytd = ctx['ytd']
    nt = NetworkTable(network)
    doylimiter = ""
    if ytd == 'yes':
        doylimiter = (" and extract(doy from valid) < "
                      " extract(doy from 'TODAY'::date) ")

    cursor.execute("""
    SELECT to_char(valid, 'YYYYmmddHH24') as d, avg(tmpf), avg(dwpf)
    from alldata WHERE station = %s and tmpf >= 80 and dwpf >= 30
    and dwpf <= tmpf and valid > '1973-01-01' """ + doylimiter + """ GROUP by d
    """, (station, ))

    rows = []
    for row in cursor:
        t = temperature(row[1], 'F')
        d = temperature(row[2], 'F')
        h = pymet.heatindex(t, d)
        if h.value('F') >= t.value('F'):
            rows.append(dict(year=int(row[0][:4]), heatindex=h.value('F')))

    minyear = max([1973, nt.sts[station]['archive_begin'].year])
    maxyear = datetime.date.today().year
    years = float((maxyear - minyear) + 1)
    df = pd.DataFrame(rows)
    x = []
    y = []
    y2 = []
    (fig, ax) = plt.subplots(1, 1)
    yloc = 0.9
    ax.text(0.7, 0.94, 'Avg:',
            transform=ax.transAxes, color='b')
    ax.text(0.85, 0.94, '%s:' % (highlightyear,),
            transform=ax.transAxes, color='r')
    for level in range(90, 121):
        x.append(level)
        y.append(len(df[df['heatindex'] >= level]) / years)
        y2.append(len(df[np.logical_and(df['heatindex'] >= level,
                                        df['year'] == highlightyear)]))
        if level % 2 == 0:
            ax.text(0.6, yloc, '%s' % (level,),
                    transform=ax.transAxes)
            ax.text(0.7, yloc, '%.1f' % (y[-1],),
                    transform=ax.transAxes, color='b')
            ax.text(0.85, yloc, '%.0f' % (y2[-1],),
                    transform=ax.transAxes, color='r')
            yloc -= 0.04
    x = np.array(x, dtype=np.float64)
    ax.scatter(x, y, color='b', label='Avg')
    ax.scatter(x, y2, color='r', label="%s" % (highlightyear,))
    ax.grid(True)
    ax.set_ylim(-0.5, int(max(y)) + 5)
    ax.set_xlim(89.5, 120.5)
    ax.set_yticks(range(0, int(max(y)), 24))
    ax.set_ylabel("Hours Per Year")
    ax.set_xlabel("Heat Index Temp $^\circ$F")
    title = 'till %s' % (datetime.date.today().strftime("%-d %b"),)
    title = "Entire Year" if ytd == 'no' else title
    ax.set_title(("[%s] %s %s-%s\n"
                  "Heat Index (when accretive to air temp) Histogram (%s)"
                  ) % (station, nt.sts[station]['name'],
                       minyear,
                       datetime.date.today().year, title))
    ax.legend(loc=(0.2, 0.8), scatterpoints=1)
    return fig, df

if __name__ == '__main__':
    plotter(dict(ytd='yes', network='IA_ASOS', zstation='DSM'))
