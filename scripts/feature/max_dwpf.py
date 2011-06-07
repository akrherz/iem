import iemdb
import random
import iemplot
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

icursor.execute("""
    SELECT station, x(geom), y(geom), max(max_tmpf) from summary_2011
    WHERE day > '2011-04-13' and max_tmpf > -50 and max_tmpf < 99  
    and network in ('IA_ASOS','MO_ASOS','KS_ASOS','NE_ASOS','SD_ASOS',
	'ND_ASOS','MN_ASOS','WI_ASOS','IL_ASOS','IN_ASOS','MI_ASOS')
    and station not in ('BAC','FAM') GROUP by station,x , y ORDER by max ASC
""")
lats = []
lons = []
data = []
for row in icursor:
    lats.append( row[2] )
    lons.append( row[1] )
    data.append( row[3] )
    
cfg = {
       '_midwest': True,
       'lbTitleString': '[F]',
       '_title': '14-25 April 2011 Maximum Air Temperature',
       #'_showvalues': True,
       #'_format': '%.0f',
 'cnLevelSelectionMode' : 'ManualLevels',
 'cnLevelSpacingF'      : 2.,
 'cnMinLevelValF'       : 54.,
 'cnMaxLevelValF'       : 84.0,

       }

fp = iemplot.simple_contour(lons, lats, data, cfg)
#iemplot.postprocess(fp,'','')
iemplot.makefeature(fp)
