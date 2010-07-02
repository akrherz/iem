# Plots of 12z precipitation please

import sys, os, random
sys.path.append("../lib/")
import iemplot, network
st = network.Table(["IA_COOP",'MO_COOP','KS_COOP','NE_COOP','SD_COOP',
     'ND_ASOS', 'MN_COOP', 'WI_COOP', 'IL_COOP','IN_COOP','OH_COOP','MI_COOP'])

import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
dbconn = i['iem']

def doit(now):
  """
  Generate some plots for the COOP data!
  """
  # We'll assume all COOP data is 12z, sigh for now
  sql = """SELECT station, pday
           from summary_%s WHERE day = '%s' and
           network ~* 'COOP' and pday >= 0""" % (now.year,
           now.strftime("%Y-%m-%d") )

  lats = []
  lons = []
  vals = []
  #labels = []
  rs = dbconn.query(sql).dictresult()
  for i in range(len(rs)):
    id = rs[i]['station']
    if not st.sts.has_key(id):
      continue
    #labels.append( id[2:] )
    lats.append( st.sts[id]['lat'] + (random.random() * 0.001))
    lons.append( st.sts[id]['lon'] )
    vals.append( rs[i]['pday'] )

    
  # Plot Iowa
  cfg = {
     'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
     'nglSpreadColorEnd'  : 2,
     '_MaskZero'          : True,
     'lbTitleString'      : "[inch]",
     '_valid'    : 'Ending %s at roughly 12Z' % (now.strftime("%d %B %Y"),),
     '_title'    : "24 Hour NWS COOP Precipitation [inch]",
  }

  tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
  pqstr = "plot ac %s0000 iowa_coop_12z_precip.png iowa_coop_12z_precip.png png" % (ts.strftime("%Y%m%d"),)
  iemplot.postprocess(tmpfp, pqstr)

  # Plot Midwest
  cfg = {
     'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
     'nglSpreadColorEnd'  : 2,
     '_MaskZero'          : True,
     '_midwest'           : True,
     'lbTitleString'      : "[inch]",
     '_valid'    : 'Ending %s at roughly 12Z' % (now.strftime("%d %B %Y"),),
     '_title'    : "24 Hour NWS COOP Precipitation [inch]",
  }

  tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
  pqstr = "plot ac %s0000 midwest_coop_12z_precip.png midwest_coop_12z_precip.png png" % (ts.strftime("%Y%m%d"),)
  iemplot.postprocess(tmpfp, pqstr)


ts = mx.DateTime.now()
if len(sys.argv) == 4:
    ts = mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) )
doit( ts )
