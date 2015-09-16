from pyiem.datatypes import speed
import psycopg2.extras
import numpy as np
import datetime
import calendar
import math
import pandas as pd
from pyiem.network import Table as NetworkTable

PDICT = {'mps': 'Meters per Second',
         'kt': 'knots',
         'kmh': 'Kilometers per Hour',
         'mph': 'Miles per Hour'}


def smooth(x, window_len=11, window='hanning'):

    s = np.r_[2*x[0]-x[window_len:1:-1], x, 2*x[-1]-x[-1:-window_len:-1]]
    w = eval('np.'+window+'(window_len)')
    y = np.convolve(w/w.sum(), s, mode='same')
    return y[window_len-1:-window_len+1]


def uv(sped, drct):
    """Convert wind speed and direction into u, v components

    Args:
      sped (float): wind speed in mps
      drct (float): wind direction in degrees north

    Returns:
      u (float): u component in mps
      v (float): v component in mps
    """
    dirr = drct * math.pi / 180.00
    u = 0. - sped * math.sin(dirr)
    v = 0. - sped * math.cos(dirr)
    return u, v


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This plot may take a while to appear!  It contains
    the approximate daily climatology of component wind speed."""
    d['arguments'] = [
        dict(type='zstation', name='station', default='DSM',
             network='IA_ASOS', label='Select Station:'),
        dict(type='select', name='units', default='mph',
             label='Wind Speed Units:', options=PDICT),

    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'AMW')
    units = fdict.get('units', 'mph')
    network = fdict.get('network', 'IA_ASOS')

    nt = NetworkTable(network)

    cursor.execute("""
    SELECT extract(doy from valid), sknt * 0.514, drct from alldata
    where station = %s and sknt >= 0 and drct >= 0
    """, (station, ))

    uwnd = np.zeros((366,), 'f')
    vwnd = np.zeros((366,), 'f')
    cnt = np.zeros((366,), 'f')
    for row in cursor:
        u, v = uv(row[1], row[2])
        uwnd[int(row[0]) - 1] += u
        vwnd[int(row[0]) - 1] += v
        cnt[int(row[0]) - 1] += 1

    u = speed(uwnd / cnt, 'MPS').value(units.upper())
    v = speed(vwnd / cnt, 'mps').value(units.upper())

    df = pd.DataFrame(dict(u=pd.Series(u),
                           v=pd.Series(v),
                           day_of_year=pd.Series(np.arange(1, 366))))

    (fig, ax) = plt.subplots(1, 1)

    ax.plot(np.arange(1, 366), smooth(u[:-1], 14, 'hamming'), color='r',
            label='u, West(+) : East(-) component')
    ax.plot(np.arange(1, 366), smooth(v[:-1], 14, 'hamming'), color='b',
            label='v, South(+) : North(-) component')
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.legend(ncol=2, fontsize=11, loc=(0., -0.15))
    ax.grid(True)
    ax.set_xlim(0, 366)
    ax.set_title(("[%s] %s Daily Average Component Wind Speed\n"
                  "[%s-%s] 14 day smooth filter applied, %.0f obs found"
                  "") % (station, nt.sts[station]['name'],
                         nt.sts[station]['archive_begin'].year,
                         datetime.datetime.now().year, np.sum(cnt)))
    ax.set_ylabel("Average Wind Speed %s" % (PDICT.get(units), ))

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width,
                     box.height * 0.9])

    return fig, df
