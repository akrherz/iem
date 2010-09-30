# Analysis of current MOS temperature bias

import sys, os
import iemplot
import iemdb

import mx.DateTime

MOS = iemdb.connect('mos', bypass=True)
IEM = iemdb.connect('iem', bypass=True)
mcursor = MOS.cursor()
icursor = IEM.cursor()

def doit(now, model):
    # Figure out the model runtime we care about
    mcursor.execute("""
    SELECT max(runtime) from alldata where station = 'KDSM'
    and ftime = %s and model = %s
    """, (now.strftime("%Y-%m-%d %H:00"), model))
    row = mcursor.fetchone()
    runtime = row[0]
    if runtime is None:
        sys.exit()
    #print "Model Runtime used: %s" % (runtime,)

    # Load up the mos forecast for our given 
    mcursor.execute("""
      SELECT station, tmp FROM alldata
    WHERE model = %s and runtime = %s and ftime = %s and tmp < 999
    """, (model, runtime, now.strftime("%Y-%m-%d %H:00") ))
    forecast = {}
    for row in mcursor:
        if row[0][0] == 'K':
            forecast[ row[0][1:] ] = row[1]

    # Load up the currents!
    icursor.execute("""
SELECT 
  station, network, tmpf, x(geom) as lon, y(geom) as lat
FROM 
  current
WHERE
  (network ~* 'ASOS' or network = 'AWOS') and 
  valid + '15 minutes'::interval > now() and
  tmpf > -50
    """)

    lats = []
    lons = []
    vals = []
    valmask = []
    for row in icursor:
        if not forecast.has_key( row[0] ):
            continue
        lats.append( row[4] )
        lons.append( row[3] )
        diff = forecast[row[0]] - row[2]
        if diff > 20 or diff < -20:
            print "Major Diff ID: %s OB: %s MOS: %s" % (row[0], row[2], 
                                                  forecast[row[0]])
        vals.append( diff )
        valmask.append(  (row[1] in ['AWOS','IA_AWOS']) )

    cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "%s MOS Temperature Bias " % (model,),
 '_midwest'     : True,
 '_valid'             : 'Model Run: %s Forecast Time: %s' % (
                                runtime.strftime("%d %b %Y %-I %p"), 
                                now.strftime("%d %b %Y %-I %p")),
 '_showvalues'        : False,
 '_format'            : '%.0f',
 '_valuemask'         : valmask,
 'lbTitleString'      : "[F]",
}
    # Generates tmp.ps
    fp = iemplot.simple_contour(lons, lats, vals, cfg)
    pqstr = "plot ac %s00 %s_mos_T_bias.png %s_mos_T_bias_%s.png png" % (
                now.gmtime().strftime("%Y%m%d%H"), model.lower(),
                model.lower(), now.gmtime().strftime("%H"))
    iemplot.postprocess(fp,pqstr)
    
    del(cfg['_midwest'])
    cfg['_conus'] = True
    fp = iemplot.simple_contour(lons, lats, vals, cfg)
    pqstr = "plot ac %s00 conus_%s_mos_T_bias.png conus_%s_mos_T_bias_%s.png png" % (
                now.gmtime().strftime("%Y%m%d%H"), model.lower(),
                model.lower(), now.gmtime().strftime("%H"))
    iemplot.postprocess(fp,pqstr)
    
if __name__ == "__main__":
    if len(sys.argv) == 6:
        doit(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4])), sys.argv[5] )
    else:
        doit( mx.DateTime.now(), sys.argv[1] )