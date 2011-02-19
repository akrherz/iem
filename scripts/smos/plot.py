# Create a plot of SMOS data for either 0 or 12z
import iemplot
import iemdb
import sys
import numpy as np
import mx.DateTime
SMOS = iemdb.connect('smos')
scursor = SMOS.cursor()

def makeplot(ts):
    """
    Generate two plots for a given time GMT
    """
    sql = """
    SELECT x(geom), y(geom), 
    CASE WHEN sm is Null THEN 0 ELSE sm END, 
    CASE WHEN od is Null THEN 0 ELSE od END from 
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
    lats = np.array( lats )
    lons = np.array( lons )
    sm = np.array( sm )
    od = np.array( od )
    
    cfg = {
            'wkColorMap': 'BlAqGrYeOrRe',
            'nglSpreadColorStart': -1,
            'nglSpreadColorEnd'  : 2,
           '_title'     : 'SMOS Satellite: Soil Moisture (0-5cm)',
           '_valid'     : "Satelite passes around %s UTC" % (ts.strftime("%d %B %Y %H"),),
           '_midwest'   : True,
           '_MaskZero'  : True,
           'cnLevelSelectionMode' : 'ManualLevels',
           'cnLevelSpacingF'      : 5.,
            'cnMinLevelValF'       : 0.,
            'cnMaxLevelValF'       : 70.,
           'lbTitleString' : '[%]'
           }
    fp = iemplot.simple_grid_fill(lons, lats, sm, cfg)
    pqstr = "plot ac %s00 smos_midwest_sm%s.png smos_midwest_sm%s.png png" % (
                ts.strftime("%Y%m%d%H"), ts.strftime("%H"),
                ts.strftime("%H"))
    iemplot.postprocess(fp, pqstr)
    del(cfg['_midwest'])
    fp = iemplot.simple_grid_fill(lons, lats, sm, cfg)
    pqstr = "plot ac %s00 smos_iowa_sm%s.png smos_iowa_sm%s.png png" % (
                ts.strftime("%Y%m%d%H"), ts.strftime("%H"),
                ts.strftime("%H"))
    iemplot.postprocess(fp, pqstr)
    
    cfg = {
           '_title': 'SMOS Satellite: Land Cover Optical Depth (microwave L-band)',
           '_valid'     : "Satelite passes around %s UTC" % (ts.strftime("%d %B %Y %H"),),
           '_midwest'   : True,
           '_MaskZero'  : True,
           'cnLevelSelectionMode' : 'ManualLevels',
           'cnLevelSpacingF'      : .05,
            'cnMinLevelValF'       : 0.,
            'cnMaxLevelValF'       : 1.,
           'lbTitleString' : ' '
    }
    fp = iemplot.simple_grid_fill(lons, lats, od, cfg)
    pqstr = "plot ac %s00 smos_midwest_od%s.png smos_midwest_od%s.png png" % (
                ts.strftime("%Y%m%d%H"), ts.strftime("%H"),
                ts.strftime("%H"))
    iemplot.postprocess(fp, pqstr)
    del(cfg['_midwest'])
    fp = iemplot.simple_grid_fill(lons, lats, od, cfg)
    pqstr = "plot ac %s00 smos_iowa_od%s.png smos_iowa_od%s.png png" % (
                ts.strftime("%Y%m%d%H"), ts.strftime("%H"),
                ts.strftime("%H"))
    iemplot.postprocess(fp, pqstr)

if __name__ == '__main__':
    # At midnight, we have 12z previous day
    # At noon, we have 0z of that day
    # Run for hour
    if len(sys.argv) == 2:
        hr = int(sys.argv[1])
        if hr == 0:
            ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1,hour=12)
        else:
            ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(hour=0)
        makeplot( ts )
    else:
        makeplot( mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), 0))