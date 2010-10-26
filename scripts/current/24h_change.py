
import iemdb
import mx.DateTime
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

icursor.execute("""
	SELECT station, x(geom) as lon, y(geom) as lat, alti from current_log
	WHERE (network ~* 'ASOS' or network = 'AWOS') and network != 'IQ_ASOS'
	and valid BETWEEN now() - '1500 minutes'::interval 
                      and now() - '1440 minutes'::interval
    and alti > 0 and alti < 40
	""")
data = {}
for row in icursor:
	data[ row[0] ] = {'lon': row[1], 'lat': row[2], 'val': row[3] }

icursor.execute("""
	SELECT station, alti from current
	WHERE (network ~* 'ASOS' or network = 'AWOS') and network != 'IQ_ASOS'
    and alti > 0 and alti < 40
	""")

obs = []
lats = []
lons = []
mask = []
for row in icursor:
	if not data.has_key(row[0]):
		continue
	v = (row[1] - data[row[0]]['val']) * 33.86
	obs.append( v )
	if v <= -24:
		mask.append( True )
	else:
		mask.append( False )
	lats.append( data[row[0]]['lat'] )
	lons.append( data[row[0]]['lon'] )

import iemplot

cfg = {
	'_midwest' : True,
	'lbTitleString' : 'mb',
	 'wkColorMap': 'BlAqGrYeOrRe',
	'_valuemask'	: mask,
	'_showvalues'	: True,
	'_format'		: '%.0f',
	'_title'	: '24 Hour Pressure Change',
	'_valid'	: '24 Hour Period Ending %s' % (mx.DateTime.now().strftime("%d %b %Y %I %p"),),
	'nglSpreadColorStart': -1,
 	'nglSpreadColorEnd'  : 2,
}
tmpfp = iemplot.simple_contour(lons, lats, obs, cfg)
pqstr = "plot c 000000000000 24h_delta_alti.png bogus png"
thumbpqstr = "plot c 000000000000 24h_delta_alti_thumb.png bogus png"
iemplot.postprocess(tmpfp,pqstr, thumb=True, thumbpqstr=thumbpqstr)

