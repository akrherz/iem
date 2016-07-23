import psycopg2.extras
import pyiem.nws.vtec as vtec
import datetime
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 3600
    d['description'] = """This map depicts the number of days since a
    Weather Forecast Office has issued a given VTEC product."""
    d['arguments'] = [
        dict(type='phenomena', name='phenomena',
             default='TO', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='W', label='Select Watch/Warning Significance Level:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    utc = datetime.datetime.utcnow()
    bins = [0, 1, 14, 31, 91, 182, 273, 365, 730, 1460, 2920, 3800]
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    phenomena = fdict.get('phenomena', 'TO')
    significance = fdict.get('significance', 'W')

    cursor.execute("""
     select wfo,  extract(days from ('TODAY'::date - max(issue))) as m
     from warnings where significance = %s and phenomena = %s
     GROUP by wfo ORDER by m ASC
    """, (significance, phenomena))
    data = {}
    rows = []
    for row in cursor:
        wfo = row[0] if row[0] != 'JSJ' else 'SJU'
        rows.append(dict(wfo=wfo, days=row[1]))
        data[wfo] = max([row[1], 0])
    df = pd.DataFrame(rows)
    df.set_index('wfo', inplace=True)

    m = MapPlot(sector='nws', axisbg='white', nocaption=True,
                title='Days since Last %s %s by NWS Office' % (
                        vtec._phenDict.get(phenomena, phenomena),
                        vtec._sigDict.get(significance, significance)),
                subtitle='Valid %s' % (utc.strftime("%d %b %Y %H%M UTC"),))
    m.fill_cwas(data, bins=bins, ilabel=True, units='Days',
                lblformat='%.0f')

    return m.fig, df
