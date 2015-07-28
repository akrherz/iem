import psycopg2.extras
import pyiem.nws.vtec as vtec
import numpy as np
import pandas as pd
from pyiem.reference import state_names
from pyiem.network import Table as NetworkTable

PDICT = {'cwa': 'Plot by NWS Forecast Office',
         'state': 'Plot by State'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This map displays the last year of a given NWS
    watch, warning, advisory was issued for a given county, parish, zone
    within a given state."""
    d['arguments'] = [
        dict(type='select', name='t', default='state', options=PDICT,
             label='Select plot extent type:'),
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO: (ignored if plotting state)'),
        dict(type='state', name='state',
             default='IA', label='Select State: (ignored if plotting wfo)'),
        dict(type='phenomena', name='phenomena',
             default='TO', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='A', label='Select Watch/Warning Significance Level:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from pyiem.plot import MapPlot
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    state = fdict.get('state', 'IA')
    phenomena = fdict.get('phenomena', 'TO')
    significance = fdict.get('significance', 'A')
    station = fdict.get('station', 'DMX')[:4]
    t = fdict.get('t', 'state')
    nt = NetworkTable("WFO")
    if t == 'cwa':
        cursor.execute("""
        select ugc, max(issue at time zone 'UTC') from warnings
        WHERE wfo = %s and phenomena = %s and significance = %s
        GROUP by ugc
        """, (station, phenomena, significance))
    else:
        cursor.execute("""
        select ugc, max(issue at time zone 'UTC') from warnings
        WHERE substr(ugc, 1, 2) = %s and phenomena = %s and significance = %s
        GROUP by ugc
        """, (state, phenomena, significance))

    rows = []
    data = {}
    for row in cursor:
        rows.append(dict(valid=row[1],
                         year=row[1].year,
                         ugc=row[0]))
        data[row[0]] = row[1].year
    df = pd.DataFrame(rows)
    bins = range(np.min(df['year'][:])-1, np.max(df['year'][:])+2, 1)
    clevstride = 1 if bins[0] > 2000 else 2
    subtitle = "based on IEM Archives of NWS WWA"
    if t == 'cwa':
        subtitle = "Plotted for %s (%s), %s" % (nt.sts[station]['name'],
                                                station, subtitle)
    else:
        subtitle = "Plotted for %s, %s" % (state_names[state],
                                           subtitle)
    m = MapPlot(sector=('state' if t == 'state' else 'cwa'),
                state=state, cwa=station, axisbg='white',
                title=('Year of Last %s %s (%s.%s)'
                       ) % (vtec._phenDict[phenomena],
                            vtec._sigDict[significance],
                            phenomena, significance),
                subtitle=subtitle, nocaption=True
                )
    cmap = plt.get_cmap('Paired')
    cmap.set_over('white')
    cmap.set_under('white')
    m.fill_ugcs(data, bins, cmap=cmap, clevstride=clevstride)
    # if t == 'cwa':
    #    m.drawcwas()
    return m.fig, df
