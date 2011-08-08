"""
Create a plot of a RTMA variable, this should be easy...
"""
import pygrib
import mx.DateTime
import iemplot

def do_hour(gts, varname):
    """
    Generate an hourly plot of RTMA
    """
    fp = gts.strftime("/mnt/a4/data/%Y/%m/%d/grib2/ncep/RTMA/%Y%m%d%H00_TMPK.grib2")
    grib = pygrib.open(fp)
    g = grib[1]
    lats, lons = g.latlons()
    total = ( g["values"] - 273.15 )  * 9.0/5.0 + 32.0
    grib.close()
    
        # Now we dance
    cfg = {
     'wkColorMap': 'BlAqGrYeOrRe',
     #'nglSpreadColorStart': -1,
     #'nglSpreadColorEnd'  : 2,
                'cnLevelSelectionMode' : 'ManualLevels',
           'cnLevelSpacingF'      : .5,
            'cnMinLevelValF'       : 60.,
            'cnMaxLevelValF'       : 80.,
     '_MaskZero'          : True,
     'lbTitleString'      : "[F]",
     '_valid'    : '%s UTC' % (
        (gts).strftime("%d %B %Y %I:%M %p"),),
     '_title'    : "NCEP 2.5km Mesoscale Analysis 2m Temperature [F]",
    }

    tmpfp = iemplot.simple_grid_fill(lons, lats, total, cfg)
    pqstr = "plot ac %s00 rtma/iowa_stage4_1d.png iowa_stage4_1d.png png" % (
            gts.strftime("%Y%m%d%H"), )
    iemplot.postprocess(tmpfp, pqstr)

    # Midwest
    cfg['_midwest'] = True
    tmpfp = iemplot.simple_grid_fill(lons, lats, total, cfg)
    pqstr = "plot ac %s00 midwest_stage4_1d.png midwest_stage4_1d.png png" % (
            gts.strftime("%Y%m%d%H"), )
    iemplot.postprocess(tmpfp, pqstr)
    del(cfg['_midwest'])

    # CONUS
    cfg['_conus'] = True
    tmpfp = iemplot.simple_grid_fill(lons, lats, total, cfg)
    pqstr = "plot ac %s00 conus_stage4_1d.png conus_stage4_1d.png png" % (
            gts.strftime("%Y%m%d%H"), )
    iemplot.postprocess(tmpfp, pqstr)
    del(cfg['_conus'])

do_hour( mx.DateTime.DateTime(2011,6,1,17,0), 'TMPK')