# 
from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']
mesosite = i['mesosite']
import scipy.stats, numpy

import sys, os
sys.path.append("../lib/")
import iemplot
import mx.DateTime

now = mx.DateTime.now()

rs = mesosite.query("""SELECT id, x(geom) as lon, y(geom) as lat from stations
  WHERE (network ~* 'ASOS' or network = 'IA_AWOS') and network not in ('IQ_ASOS','PA_ASOS')""").dictresult()

lats = []
lons = []
vals = []
for i in range(len(rs)):
  rs2 = iem.query("""select one.day, one.max_tmpf as ames, 
        two.max_tmpf as other from (select day, max_tmpf from summary_2010 
        where station = 'AMW' and max_tmpf > -30) as one, 
        (select day, max_tmpf from summary_2010 where station = '%s' and 
         max_tmpf > -30) as two WHERE two.day = one.day ORDER by one.day ASC""" % (rs[i]['id'],)
        ).dictresult()
  ames = numpy.zeros( len(rs2), 'f')
  other = numpy.zeros( len(rs2), 'f')
  for j in range(len(rs2)):
    ames[j] = rs2[j]['ames'] 
    other[j] = rs2[j]['other'] 
  if len(ames) > 31:
    #if scipy.stats.corrcoef(ames, other)[0,1] < 0.86:
    #  print rs[i]['id'], scipy.stats.corrcoef(ames, other)[0,1]
    #  continue
    vals.append( scipy.stats.corrcoef(ames, other)[0,1] )
    lats.append( rs[i]['lat'] )
    lons.append( rs[i]['lon'] )

cfg = {
 'wkColorMap': 'WhViBlGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 
# 'cnLevelSelectionMode' : 'ManualLevels',
# 'cnLevelSpacingF'      : .5,
# 'cnMinLevelValF'       : .5,
# 'cnMaxLevelValF'       : 8.0,
 
# '_valuemask'         : valmask,
 '_conus'           : True,
 '_title'             : "2010 Ames High Temperature Correlation",
 '_valid'             : "Valid: 1 Jan - "+ now.strftime("%d %b %Y"),
# '_showvalues'        : True,
# '_format'            : '%.0f',
 'lbTitleString'      : "Cor",
}

fp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.postprocess(fp, "")

