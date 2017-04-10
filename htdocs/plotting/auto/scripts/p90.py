import psycopg2.extras
import pyiem.nws.vtec as vtec
import numpy as np
import datetime
import pytz
from rasterstats import zonal_stats
import pandas as pd
from affine import Affine
from pyiem.reference import state_names, state_bounds, wfo_bounds
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context
from geopandas import read_postgis

PDICT = {'cwa': 'Plot by NWS Forecast Office',
         'state': 'Plot by State'}
PDICT2 = {'total': 'Total Count between Start and End Date',
          'yearcount': 'Count of Events for Given Year',
          'yearavg': 'Yearly Average Count between Start and End Year',
          'lastyear': 'Year of Last Issuance'}
PDICT3 = {'yes': 'YES: Label Counties/Zones',
          'no': 'NO: Do not Label Counties/Zones'}
PDICT4 = {'ugc': 'Summarize/Plot by UGC (Counties/Parishes/Zones)',
          'polygon': 'Summarize/Plot by Polygon (Storm Based Warnings)'}
PDICT5 = {'yes': 'YES: Draw Counties/Parishes',
          'no': 'NO: Do Not Draw Counties/Parishes'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This application has a considerable and likely
    confusing amount of configuration options.  In general, it will produce
    a map of either a single NWS Weather Forecast Office (WFO) or for a
    specified state.  For warning types that are issued with polygons, you
    can optionally plot heatmaps of these products.  Please be careful when
    selecting start and end dates to ensure you are getting the plot you
    want.  There are likely some combinations here that will produce a
    broken image symbol.  If you find such a case, please email us the link
    to this page that shows the broken image!

    <br />Storm Based Warning polygons were not official until 1 October 2007,
    so if you generate plots for years prior to this date, you may notice
    polygons well outside the County Warning Area bounds.  There was no
    enforcement of these unofficial polygons to stay within CWA bounds.

    <br /><strong>This app can be very slow</strong>, so please let it grind
    away as sometimes it will take 3-5 minutes to generate a map :("""
    today = datetime.date.today()
    jan1 = today.replace(day=1, month=1)
    d['arguments'] = [
        dict(type='select', name='t', default='state', options=PDICT,
             label='Select plot extent type:'),
        dict(type='select', name='v', default='lastyear', options=PDICT2,
             label='Select statistic to plot:'),
        dict(type='select', name='ilabel', default='yes', options=PDICT3,
             label='Overlay values on map?'),
        dict(type='select', name='geo', default='ugc', options=PDICT4,
             label='Plot by UGC (Counties/Parishes/Zones) or Polygons?'),
        dict(type='select', name='drawc', default='yes', options=PDICT5,
             label='Plot County/Parish borders on polygon summary maps?'),
        dict(type='year', min=1986, name='year', default=today.year,
             label='Select start year (where appropriate):'),
        dict(type='year', min=1986, name='year2', default=today.year,
             label='Select end year (inclusive, where appropriate):'),
        dict(type='date', name='sdate',
             default=jan1.strftime("%Y/%m/%d"),
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


def do_polygon(ctx):
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    varname = ctx['v']
    station = ctx['station'][:4]
    state = ctx['state']
    phenomena = ctx['phenomena']
    significance = ctx['significance']
    t = ctx['t']
    sdate = ctx['sdate']
    edate = ctx['edate']
    year = ctx['year']
    year2 = ctx['year2']
    # figure out the start and end timestamps
    if varname == 'total':
        sts = sdate
        ets = edate
    elif varname == 'yearcount':
        sts = datetime.datetime(year, 1, 1).replace(tzinfo=pytz.utc)
        ets = datetime.datetime(year, 12, 31, 23, 59).replace(tzinfo=pytz.utc)
    else:
        sts = datetime.datetime(year, 1, 1).replace(tzinfo=pytz.utc)
        ets = datetime.datetime(year2, 12, 31, 23, 59).replace(tzinfo=pytz.utc)
    # We need to figure out how to get the warnings either by state or by wfo
    if t == 'cwa':
        (west, south, east, north) = wfo_bounds[station]
    else:
        (west, south, east, north) = state_bounds[state]
    # buffer by 5 degrees so to hopefully get all polys
    (west, south) = [x - 2 for x in (west, south)]
    (east, north) = [x + 2 for x in (east, north)]
    # create grids
    griddelta = 0.01
    lons = np.arange(west, east, griddelta)
    lats = np.arange(south, north, griddelta)
    YSZ = len(lats)
    XSZ = len(lons)
    lons, lats = np.meshgrid(lons, lats)
    affine = Affine(griddelta, 0., west, 0., 0 - griddelta, north)
    ones = np.ones((int(YSZ), int(XSZ)))
    counts = np.zeros((int(YSZ), int(XSZ)))
    wfolimiter = ""
    if ctx['t'] == 'cwa':
        wfolimiter = " wfo = '%s' and " % (station, )
    # do arbitrary buffer to prevent segfaults?
    df = read_postgis("""
    SELECT ST_Forcerhr(ST_Buffer(geom, 0.0005)) as geom, issue, expire
     from sbw where """ + wfolimiter + """
     phenomena = %s and status = 'NEW' and significance = %s
     and ST_Within(geom, ST_GeomFromEWKT('SRID=4326;POLYGON((%s %s, %s %s,
     %s %s, %s %s, %s %s))')) and ST_IsValid(geom)
     and issue >= %s and issue <= %s ORDER by issue ASC
    """, pgconn, params=(phenomena, significance, west, south, west, north,
                         east, north, east, south, west, south, sts, ets),
                      geom_col='geom', index_col=None)
    # print df, sts, ets, west, east, south, north
    zs = zonal_stats(df['geom'], ones, affine=affine, nodata=-1,
                     all_touched=True, raster_out=True)
    for i, z in enumerate(zs):
        aff = z['mini_raster_affine']
        mywest = aff.c
        mynorth = aff.f
        raster = np.flipud(z['mini_raster_array'])
        x0 = int((mywest - west) / griddelta)
        y1 = int((mynorth - south) / griddelta)
        dy, dx = np.shape(raster)
        x1 = x0 + dx
        y0 = y1 - dy
        if x0 < 0 or x1 >= XSZ or y0 < 0 or y1 >= YSZ:
            # print raster.mask.shape, west, x0, x1, XSZ, north, y0, y1, YSZ
            continue
        if varname == 'lastyear':
            counts[y0:y1, x0:x1] = np.where(raster.mask, counts[y0:y1, x0:x1],
                                            df.iloc[i]['issue'].year)
        else:
            counts[y0:y1, x0:x1] += np.where(raster.mask, 0, 1)
    if np.max(counts) == 0:
        raise Exception("Sorry, no data found for query!")
    # construct the df
    ctx['df'] = pd.DataFrame({'lat': lats.ravel(),
                              'lon': lons.ravel(),
                              'val': counts.ravel()})
    minv = df['issue'].min()
    maxv = df['issue'].max()
    if varname == 'lastyear':
        ctx['title'] = "Year of Last"
        if (maxv.year - minv.year) < 3:
            bins = range(int(minv.year) - 4, int(maxv.year) + 2)
        else:
            bins = range(int(minv.year), int(maxv.year) + 2)
    elif varname == 'yearcount':
        ctx['title'] = "Count for %s" % (year,)
    elif varname == 'total':
        ctx['title'] = "Total between %s and %s" % (sdate.strftime("%d %b %Y"),
                                                    edate.strftime("%d %b %Y"))
    elif varname == 'yearavg':
        ctx['title'] = ("Yearly Avg: %s and %s"
                        ) % (minv.strftime("%d %b %Y"),
                             maxv.strftime("%d %b %Y"))
        years = (maxv.year - minv.year) + 1
        counts = counts / years

    minv = np.min(counts)
    maxv = np.max(counts)
    if varname != 'lastyear':
        for delta in [500, 50, 5, 1, 0.5, 0.05]:
            bins = np.arange(0, maxv * 1.05, delta)
            if len(bins) > 8:
                break
        bins[0] = 0.01
    ctx['bins'] = bins
    ctx['data'] = counts
    ctx['lats'] = lats
    ctx['lons'] = lons


def do_ugc(ctx):
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    varname = ctx['v']
    station = ctx['station'][:4]
    state = ctx['state']
    phenomena = ctx['phenomena']
    significance = ctx['significance']
    t = ctx['t']
    sdate = ctx['sdate']
    edate = ctx['edate']
    year = ctx['year']
    year2 = ctx['year2']
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
        ctx['title'] = "Year of Last"
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
        ctx['title'] = "Count for %s" % (year,)
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
        ctx['title'] = "Total between %s and %s" % (sdate.strftime("%d %b %Y"),
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
        ctx['title'] = ("Yearly Avg: %s and %s"
                        ) % (minv.strftime("%d %b %Y"),
                             maxv.strftime("%d %b %Y"))
        datavar = "average"

    if len(rows) == 0:
        raise Exception("Sorry, no data found for query!")
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
    ctx['bins'] = bins
    ctx['data'] = data
    ctx['df'] = df


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from pyiem.plot import MapPlot
    ctx = get_autoplot_context(fdict, get_description())
    state = ctx['state']
    phenomena = ctx['phenomena']
    significance = ctx['significance']
    station = ctx['station'][:4]
    t = ctx['t']
    ilabel = (ctx['ilabel'] == 'yes')
    geo = ctx['geo']
    nt = NetworkTable("WFO")
    if geo == 'ugc':
        do_ugc(ctx)
    elif geo == 'polygon':
        do_polygon(ctx)

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
                       ) % (ctx['title'], vtec._phenDict[phenomena],
                            vtec._sigDict[significance],
                            phenomena, significance),
                subtitle=subtitle, nocaption=True,
                titlefontsize=16
                )
    if geo == 'ugc':
        cmap = plt.get_cmap('Paired')
        cmap.set_under('white')
        cmap.set_over('white')
        m.fill_ugcs(ctx['data'], ctx['bins'], cmap=cmap, ilabel=ilabel)
    else:
        cmap = plt.get_cmap('jet')
        cmap.set_under('white')
        cmap.set_over('black')
        res = m.pcolormesh(ctx['lons'], ctx['lats'], ctx['data'],
                           ctx['bins'], cmap=cmap, units='count')
        # Cut down on SVG et al size
        res.set_rasterized(True)
        if ctx['drawc'] == 'yes':
            m.drawcounties()

    return m.fig, ctx['df']


if __name__ == '__main__':
    plotter(dict(geo='polygon', state='NM', phenomena='SV',
                 significance='W', v='lastyear', year=1986, year2=2017))
