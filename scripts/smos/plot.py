"""Create a plot of SMOS data for either 0 or 12z"""
import matplotlib
matplotlib.use('agg')
from pyiem.plot import MapPlot
import psycopg2
import sys
import numpy as np
import mx.DateTime
import matplotlib.cm as cm
SMOS = psycopg2.connect(database='smos', host='iemdb', user='nobody')
scursor = SMOS.cursor()


def makeplot(ts, routes='ac'):
    """
    Generate two plots for a given time GMT
    """
    sql = """
    SELECT ST_x(geom), ST_y(geom), 
    CASE WHEN sm is Null THEN -1 ELSE sm END, 
    CASE WHEN od is Null THEN -1 ELSE od END from 
     (SELECT grid_idx, avg(soil_moisture) as sm,
     avg(optical_depth) as od
     from data WHERE valid > '%s+00'::timestamptz - '6 hours'::interval
     and valid < '%s+00'::timestamptz + '6 hours'::interval 
     GROUP by grid_idx) as foo, grid
     WHERE foo.grid_idx = grid.idx
    """ % (ts.strftime('%Y-%m-%d %H:%M'), 
           ts.strftime('%Y-%m-%d %H:%M'))
    #sql = """
    #SELECT x(geom), y(geom), random(), random() from grid
    #"""
    scursor.execute( sql )
    lats = []
    lons = []
    sm   = []
    od   = []
    for row in scursor:
        lats.append( float(row[1]) )
        lons.append( float(row[0]) )
        sm.append( row[2] * 100.)
        od.append( row[3] )
    if len(lats) == 0:
        # print 'Did not find SMOS data for ts: %s' % (ts,)
        return
    lats = np.array(lats)
    lons = np.array(lons)
    sm = np.array(sm)
    od = np.array(od)

    for sector in ['midwest', 'iowa']:
        clevs = np.arange(0, 71, 5)
        m = MapPlot(sector=sector, axisbg='white',
                    title='SMOS Satellite: Soil Moisture (0-5cm)',
                    subtitle="Satelite passes around %s UTC" % (
                                                ts.strftime("%d %B %Y %H"),))
        if sector == 'iowa':
            m.drawcounties()
        cmap = cm.get_cmap('jet_r')
        cmap.set_under('#EEEEEE')
        cmap.set_over("k")
        m.hexbin(lons, lats, sm, clevs, units='%', cmap=cmap)
        pqstr = "plot %s %s00 smos_%s_sm%s.png smos_%s_sm%s.png png" % (
                    routes, ts.strftime("%Y%m%d%H"), sector, ts.strftime("%H"),
                    sector, ts.strftime("%H"))
        m.postprocess(pqstr=pqstr)
        m.close()

    for sector in ['midwest', 'iowa']:
        clevs = np.arange(0, 1.001, 0.05)
        m = MapPlot(sector=sector, axisbg='white',
                    title=('SMOS Satellite: Land Cover Optical Depth '
                           '(microwave L-band)'),
                    subtitle="Satelite passes around %s UTC" % (
                                                ts.strftime("%d %B %Y %H"),))
        if sector == 'iowa':
            m.drawcounties()
        cmap = cm.get_cmap('jet')
        cmap.set_under('#EEEEEE')
        cmap.set_over("k")
        m.hexbin(lons, lats, od, clevs, cmap=cmap)
        pqstr = "plot %s %s00 smos_%s_od%s.png smos_%s_od%s.png png" % (
                    routes, ts.strftime("%Y%m%d%H"), sector, ts.strftime("%H"),
                    sector, ts.strftime("%H"))
        m.postprocess(pqstr=pqstr)
        m.close()


def main():
    """Go Main Go"""
    # At midnight, we have 12z previous day
    # At noon, we have 0z of that day
    # Run for hour
    if len(sys.argv) == 2:
        hr = int(sys.argv[1])
        if hr == 0:
            ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1,
                                                                  hour=12)
        else:
            ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(hour=0)
        makeplot(ts)
        # Run a day, a week ago ago as well
        for d in [1, 5]:
            ts -= mx.DateTime.RelativeDateTime(days=d)
            makeplot(ts, 'a')
    else:
        makeplot(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]),
                                      int(sys.argv[3]), int(sys.argv[4]), 0),
                 'a')

if __name__ == '__main__':
    main()
