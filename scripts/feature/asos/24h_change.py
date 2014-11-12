
import iemdb
import mx.DateTime
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

icursor.execute("""
	SELECT id, ST_x(geom) as lon, ST_y(geom) as lat, tmpf from current_log c JOIN stations s on (s.iemid = c.iemid)
	WHERE (network ~* 'ASOS' or network = 'AWOS') and country = 'US'
	and valid BETWEEN '2014-11-10 12:45'
                      and '2014-11-10 13:15'
    and  tmpf > 0 
	""")
data = {}
print icursor.rowcount
for row in icursor:
	data[ row[0] ] = {'lon': row[1], 'lat': row[2], 'val': row[3] }

icursor.execute("""
	SELECT id, max(tmpf) from current_log c JOIN stations s ON (s.iemid = c.iemid)
	WHERE (network ~* 'ASOS' or network = 'AWOS') and country = 'US' 
    and state not in ('AK','HI')
    and  tmpf > 0  and valid BETWEEN '2014-11-11 12:45' and '2014-11-11 13:15'
    GROUP by id
	""")
print icursor.rowcount

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
 'cnLevelSelectionMode': 'ExplicitLevels',
 'cnLevels' : range(-50,51,10),
	'_format'		: '%.0f',
	'_title'	: '24 Hour Temperature Change',
	'_valid'	: '24 Hour Period Ending 1 PM 11 Nov 2014',
}
tmpfp = iemplot.simple_contour(lons, lats, obs, cfg)
iemplot.makefeature(tmpfp)
