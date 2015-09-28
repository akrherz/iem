import psycopg2.extras
import pyiem.nws.vtec as vtec
import numpy as np
from pyiem.network import Table as NetworkTable
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 86400
    d['data'] = True
    d['description'] = """This chart presents a histogram of issuance times
    for a given watch, warning, or advisory type for a given office."""
    d['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:'),
        dict(type='phenomena', name='phenomena',
             default='WC', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='W', label='Select Watch/Warning Significance Level:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    wfo = fdict.get('station', 'DMX')
    phenomena = fdict.get('phenomena', 'WC')
    significance = fdict.get('significance', 'W')

    nt = NetworkTable("WFO")

    (fig, ax) = plt.subplots(1, 1)

    tzname = nt.sts[wfo]['tzname']
    cursor.execute("""
    WITH data as (
     SELECT extract(year from issue) as yr, eventid,
     min(issue at time zone %s) as minissue from warnings WHERE
     phenomena = %s and significance = %s
     and wfo = %s GROUP by yr, eventid)

    SELECT extract(hour from minissue) as hr, count(*) from data GROUP by hr
    """, (tzname, phenomena, significance, wfo))
    if cursor.rowcount == 0:
        ax.text(0.5, 0.5, "No Results Found",
                transform=ax.transAxes, ha='center')
        return fig

    data = np.zeros((24,), 'f')
    for row in cursor:
        data[int(row[0])] = row[1]
    df = pd.DataFrame(dict(hour=pd.Series(np.arange(24)),
                           count=pd.Series(data)))

    ax.bar(np.arange(24) - 0.4, data / float(sum(data)) * 100., ec='b', fc='b')
    ax.grid()
    ax.set_xticks(range(0, 25, 1))
    ax.set_xlim(-0.5, 23.5)
    ax.set_xticklabels(["Mid", "", "", "3 AM", "", "", "6 AM", "", "", '9 AM',
                        "", "", "Noon", "", "", "3 PM", "", "", "6 PM",
                        "", "", "9 PM", "", "", "Mid"])
    ax.set_xlabel("Timezone: %s (Daylight or Standard)" % (tzname,))
    ax.set_ylabel("Frequency [%%] out of %.0f Events" % (sum(data),))
    ax.set_title(("[%s] %s :: Issuance Time Frequency\n%s %s (%s.%s)"
                  ) % (wfo, nt.sts[wfo]['name'], vtec._phenDict[phenomena],
                       vtec._sigDict[significance], phenomena, significance))

    return fig, df
