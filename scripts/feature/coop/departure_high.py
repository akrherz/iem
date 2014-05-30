import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

# Fetch obs
icursor.execute("""
 SELECT s.climate_site, x(s.geom) as lon, y(s.geom) as lat, max_tmpf, s.id,
 s.state
 from stations s JOIN summary_2012 t ON (t.iemid = s.iemid) and
 t.day = '2012-01-05' and s.state in ('IA','MN','WI','MI','IN','IL',
 'MO','KS','NE','ND','SD') and (s.network ~* 'ASOS' or s.network = 'AWOS')
 and max_tmpf > 0
""")

lats = []
lons = []
diff = []
for row in icursor:
    #if row[5] != "IA":
    #    continue
    ccursor.execute("""
    SELECT max_high from climate where station = %s and valid = '2000-01-05'
    """, (row[0],))
    row2 = ccursor.fetchone()
    off = row[3] - row2[0]
    if row[4] == 'ABR':
        print row[4], row[3], row2[0], off
    diff.append( off )
    lats.append( row[2] )
    lons.append( row[1] )
    
import iemplot

cfg = {
       '_title': '5 Jan 2012 High Temperature Departure from Record High',
       '_valid': 'ASOS/AWOS Observations compared against long term climate',
      '_showvalues': True,
      '_format': '%.0f',
      'wkColorMap' : "BlWhRe",
      'cnLevelSelectionMode' : 'ManualLevels',
      'cnLevelSpacingF'      : 2,
     'cnMinLevelValF'       : -15,
     'cnMaxLevelValF'       : 15,
     'lbTitleString' : '[F]',
     '_midwest': True,
       }

tmpfp = iemplot.simple_contour(lons, lats, diff, cfg)
iemplot.makefeature(tmpfp)