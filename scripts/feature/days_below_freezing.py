import iemdb
#COOP = iemdb.connect('coop', bypass=True)
#ccursor = COOP.cursor()

#ccursor.execute("""
# SELECT station, avg(sum) from
# (SELECT station, extract(year from day + '3 months'::interval) as yr, 
# sum(case when high < 32 then 1 else 0 end) from alldata WHERE 
# month in (10,11,12,1) and substr(station,3,1) != 'C' and
# substr(station,4,4) != '0000' GROUP by station, yr) as foo 
# GROUP by station
#""")
#
#for row in ccursor:
#    print "%s,%s" % (row[0],row[1])

IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

climate = {}
for line in open('/tmp/coop2.txt'):
    tokens = line.split(",")
    climate[tokens[0]] = float(tokens[1])

icursor.execute("""
 SELECT stations.id, foo.sum, stations.climate_site, x(stations.geom), y(stations.geom),
 stations.network from
 (select t.iemid, sum(case when max_tmpf < 32  and max_tmpf > -60 then 1 else 0 end) from 
 summary s JOIN stations t on (t.iemid = s.iemid) 
 WHERE day > '2011-10-01'  and (t.network ~* 'ASOS' or t.network = 'AWOS') and 
 t.state in ('IA','MN','WI','MI','OH','IN','IL','MO','KS','NE','SD','ND','MN') 
 and t.country = 'US'
 GROUP by t.iemid) as foo JOIN stations ON (stations.iemid = foo.iemid)
""")
vals = []
lats = []
lons = []
for row in icursor:
    if not climate.has_key(row[2]):
        continue
    if row[4] in lats:
        continue
    diff = row[1] - climate[row[2]]
    if diff > 40 or diff < -38:
        print row
        continue
    if diff > 0 and row[5] == 'MN_ASOS':
        continue
    if diff < -30 and row[5] == 'WI_ASOS':
        continue
    vals.append( diff )
    lats.append( row[4] )
    lons.append( row[3] )
    
import iemplot
cfg = {
       'wkColorMap' : "posneg_1",
       '_midwest': True,
       'lbTitleString': 'Days',
       '_showvalues': False,
       '_format' : '%.0f',
       '_title' : 'Days Below Freezing Departure From Average',
       '_valid' : '1 October 2011 to 29 Jan 2012',
       'nglSpreadColorStart': -1,
'nglSpreadColorEnd': 3,
'cnLevelSelectionMode' : 'ManualLevels',

             'cnLevelSpacingF'      : 5,
     'cnMinLevelValF'       : -50,
     'cnMaxLevelValF'       : 50,

       }
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)
