
import iemdb
import mx.DateTime
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

icursor.execute("""
	SELECT id, x(geom) as lon, y(geom) as lat, tmpf from current_log c JOIN stations s on (s.iemid = c.iemid)
	WHERE (network ~* 'ASOS' or network = 'AWOS') and country = 'US'
	and valid BETWEEN now() - '1500 minutes'::interval 
                      and now() - '1440 minutes'::interval
    and  tmpf > 0 
	""")
data = {}
for row in icursor:
	data[ row[0] ] = {'lon': row[1], 'lat': row[2], 'val': row[3] }

icursor.execute("""
	SELECT id, tmpf from current c JOIN stations s ON (s.iemid = c.iemid)
	WHERE (network ~* 'ASOS' or network = 'AWOS') and country = 'US' 
    and state not in ('AK','HI')
    and  tmpf > 0  and valid > now() - '60 minutes'::interval
	""")

obs = []
lats = []
lons = []
mask = []
for row in icursor:
	if not data.has_key(row[0]):
		continue
	v = (row[1] - data[row[0]]['val'])
	obs.append( v )
	#if v <= -24.:
	#	mask.append( True )
	#else:
	mask.append( False )
	lats.append( data[row[0]]['lat'] )
	lons.append( data[row[0]]['lon'] )

import iemplot

cfg = {
	'_conus' : True,
	'lbTitleString' : 'F',
	 'wkColorMap': 'BlAqGrYeOrRe',
	'_valuemask'	: mask,
	'_showvalues'	: True,
	'_format'		: '%.0f',
	'_title'	: '24 Hour Temperature Change',
	'_valid'	: '24 Hour Period Ending %s' % (mx.DateTime.now().strftime("%d %b %Y %I %p"),),
}
tmpfp = iemplot.simple_contour(lons, lats, obs, cfg)
iemplot.makefeature(tmpfp)
