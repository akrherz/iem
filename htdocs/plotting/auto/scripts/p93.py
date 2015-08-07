import psycopg2.extras
from pyiem.network import Table as NetworkTable
import numpy as np
import pandas as pd
import datetime
from pyiem.datatypes import temperature
import pyiem.meteorology as pymet


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
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('zstation', 'DSM')
    network = fdict.get('network', 'IA_ASOS')
    highlightyear = int(fdict.get('year', 2015))
    nt = NetworkTable(network)

    cursor.execute("""
    SELECT to_char(valid, 'YYYYmmddHH24') as d, avg(tmpf), avg(dwpf)
    from alldata WHERE station = %s and tmpf >= 80 and dwpf >= 30
    and dwpf <= tmpf and valid > '1973-01-01' GROUP by d
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
            transform=ax.transAxes, color='r')
    ax.text(0.85, 0.94, '%s:' % (highlightyear,),
            transform=ax.transAxes, color='b')
    for level in range(90, 121):
        x.append(level)
        y.append(len(df[df['heatindex'] >= level]) / years)
        y2.append(len(df[np.logical_and(df['heatindex'] >= level,
                                        df['year'] == highlightyear)]))
        if level % 2 == 0:
            ax.text(0.6, yloc, '%s' % (level,),
                    transform=ax.transAxes)
            ax.text(0.7, yloc, '%.1f' % (y[-1],),
                    transform=ax.transAxes, color='r')
            ax.text(0.85, yloc, '%.0f' % (y2[-1],),
                    transform=ax.transAxes, color='b')
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
    ax.set_title(("[%s] %s %s-%s\n"
                  "Heat Index (when accretive to air temp) Histogram"
                  ) % (station, nt.sts[station]['name'],
                       minyear,
                       datetime.date.today().year))
    ax.legend(loc=(0.2, 0.8), scatterpoints=1)
    return fig, df
