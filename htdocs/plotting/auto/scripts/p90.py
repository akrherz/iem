import psycopg2.extras
import pyiem.nws.vtec as vtec
import numpy as np
import datetime
import pandas as pd
from pyiem.reference import state_names
from pyiem.network import Table as NetworkTable

PDICT = {'cwa': 'Plot by NWS Forecast Office',
         'state': 'Plot by State'}
PDICT2 = {'lastyear': 'Year of Last Issuance for UGC',
          'yearcount': 'Count of Events for Given Year',
          'yearavg': 'Yearly Average Count between Start and End Year',
          'total': 'Total Count between Start and End Date'}
PDICT3 = {'yes': 'YES: Label Counties/Zones',
          'no': 'NO: Do not Label Counties/Zones'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This map displays map statistics a given NWS
    watch, warning, advisory was issued for a given county, parish, zone
    within a given state or given County Warning Area (CWA)."""
    today = datetime.date.today()
    d['arguments'] = [
        dict(type='select', name='t', default='state', options=PDICT,
             label='Select plot extent type:'),
        dict(type='select', name='v', default='lastyear', options=PDICT2,
             label='Select statistic to plot:'),
        dict(type='select', name='ilabel', default='yes', options=PDICT3,
             label='Overlay values on map?'),
        dict(type='year', min=1986, name='year', default=today.year,
             label='Select start year (where appropriate):'),
        dict(type='year', min=1986, name='year2', default=today.year,
             label='Select end year (inclusive, where appropriate):'),
        dict(type='date', name='sdate',
             default=today.strftime("%Y/%m/%d"),
             label='Start Date (for "total" option):', min="1986/01/01"),
        dict(type='date', name='edate',
             default=today.strftime("%Y/%m/%d"),
             label='End Date (not inclusive, for "total" option):',
             min="1986/01/01"),
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
    sdate = datetime.datetime.strptime(fdict.get('sdate', '2015-01-01'),
                                       '%Y-%m-%d')
    edate = datetime.datetime.strptime(fdict.get('edate', '2015-01-01'),
                                       '%Y-%m-%d')
    t = fdict.get('t', 'state')
    varname = fdict.get('v', 'lastyear')
    year = int(fdict.get('year', 2015))
    year2 = int(fdict.get('year2', 2015))
    ilabel = (fdict.get('ilabel', 'no') == 'yes')
    nt = NetworkTable("WFO")
    if varname == 'lastyear':
        if t == 'cwa':
            cursor.execute("""
            select ugc, max(issue at time zone 'UTC') from warnings
            WHERE wfo = %s and phenomena = %s and significance = %s
            GROUP by ugc
            """, (station if len(station) == 3 else station[1:],
                  phenomena, significance))
        else:
            cursor.execute("""
            select ugc, max(issue at time zone 'UTC') from warnings
            WHERE substr(ugc, 1, 2) = %s and phenomena = %s
            and significance = %s GROUP by ugc
            """, (state, phenomena, significance))
        rows = []
        data = {}
        for row in cursor:
            rows.append(dict(valid=row[1],
                             year=row[1].year,
                             ugc=row[0]))
            data[row[0]] = row[1].year
        title = "Year of Last"
        datavar = "year"
    elif varname == 'yearcount':
        table = "warnings_%s" % (year, )
        if t == 'cwa':
            cursor.execute("""
            select ugc, count(*) from """ + table + """
            WHERE wfo = %s and phenomena = %s and significance = %s
            GROUP by ugc
            """, (station if len(station) == 3 else station[1:],
                  phenomena, significance))
        else:
            cursor.execute("""
            select ugc, count(*) from """ + table + """
            WHERE substr(ugc, 1, 2) = %s and phenomena = %s
            and significance = %s GROUP by ugc
            """, (state, phenomena, significance))
        rows = []
        data = {}
        for row in cursor:
            rows.append(dict(count=row[1], year=year,
                             ugc=row[0]))
            data[row[0]] = row[1]
        title = "Count for %s" % (year,)
        datavar = "count"
    elif varname == 'total':
        table = "warnings"
        if t == 'cwa':
            cursor.execute("""
            select ugc, count(*), min(issue at time zone 'UTC'),
            max(issue at time zone 'UTC') from """ + table + """
            WHERE wfo = %s and phenomena = %s and significance = %s
            and issue >= %s and issue <= %s
            GROUP by ugc
            """, (station if len(station) == 3 else station[1:],
                  phenomena, significance,
                  sdate, edate))
        else:
            cursor.execute("""
            select ugc, count(*), min(issue at time zone 'UTC'),
            max(issue at time zone 'UTC') from """ + table + """
            WHERE substr(ugc, 1, 2) = %s and phenomena = %s
            and significance = %s and issue >= %s and issue < %s
            GROUP by ugc
            """, (state, phenomena, significance,
                  sdate, edate))
        rows = []
        data = {}
        for row in cursor:
            rows.append(dict(count=row[1], year=year,
                             ugc=row[0], minissue=row[2], maxissue=row[3]))
            data[row[0]] = row[1]
        title = "Total between %s and %s" % (sdate.strftime("%d %b %Y"),
                                             edate.strftime("%d %b %Y"))
        datavar = "count"
    elif varname == 'yearavg':
        table = "warnings"
        if t == 'cwa':
            cursor.execute("""
            select ugc, count(*), min(issue at time zone 'UTC'),
            max(issue at time zone 'UTC') from """ + table + """
            WHERE wfo = %s and phenomena = %s and significance = %s
            and issue >= %s and issue <= %s
            GROUP by ugc
            """, (station if len(station) == 3 else station[1:],
                  phenomena, significance,
                  datetime.date(year, 1, 1), datetime.date(year2 + 1, 1, 1)))
        else:
            cursor.execute("""
            select ugc, count(*), min(issue at time zone 'UTC'),
            max(issue at time zone 'UTC') from """ + table + """
            WHERE substr(ugc, 1, 2) = %s and phenomena = %s
            and significance = %s and issue >= %s and issue < %s
            GROUP by ugc
            """, (state, phenomena, significance,
                  datetime.date(year, 1, 1), datetime.date(year2 + 1, 1, 1)))
        rows = []
        data = {}
        minv = datetime.datetime(2050, 1, 1)
        maxv = datetime.datetime(1986, 1, 1)
        for row in cursor:
            if row[2] < minv:
                minv = row[2]
            if row[3] > maxv:
                maxv = row[3]
            rows.append(dict(count=row[1], year=year,
                             ugc=row[0], minissue=row[2], maxissue=row[3]))
            data[row[0]] = row[1]
        title = ("Yearly Avg: %s and %s"
                 ) % (minv.strftime("%d %b %Y"), maxv.strftime("%d %b %Y"))
        datavar = "average"

    if len(rows) == 0:
        return("Sorry, no data found for query!")
    df = pd.DataFrame(rows)
    if varname == 'yearavg':
        years = maxv.year - minv.year + 1
        df['average'] = df['count'] / years
        for key in data:
            data[key] = round(data[key] / float(years), 2)
        bins = range(0, int(np.max(df[datavar][:]))+2, 1)
    else:
        bins = range(np.min(df[datavar][:]), np.max(df[datavar][:])+2, 1)
    if len(bins) < 3:
        bins.append(bins[-1]+1)
    if len(bins) > 8:
        bins = np.linspace(np.min(df[datavar][:]), np.max(df[datavar][:])+2,
                           8, dtype='i')
    subtitle = "based on IEM Archives of NWS WWA"
    if t == 'cwa':
        subtitle = "Plotted for %s (%s), %s" % (nt.sts[station]['name'],
                                                station, subtitle)
    else:
        subtitle = "Plotted for %s, %s" % (state_names[state],
                                           subtitle)
    m = MapPlot(sector=('state' if t == 'state' else 'cwa'),
                state=state,
                cwa=(station if len(station) == 3 else station[1:]),
                axisbg='white',
                title=('%s %s %s (%s.%s)'
                       ) % (title, vtec._phenDict[phenomena],
                            vtec._sigDict[significance],
                            phenomena, significance),
                subtitle=subtitle, nocaption=True,
                titlefontsize=16
                )
    cmap = plt.get_cmap('Paired')
    cmap.set_over('white')
    cmap.set_under('white')
    m.fill_ugcs(data, bins, cmap=cmap, ilabel=ilabel)

    return m.fig, df
