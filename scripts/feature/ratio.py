import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

import network
nt = network.Table(("IACLIMATE", "MNCLIMATE", "NDCLIMATE", "SDCLIMATE",
 "NECLIMATE", "KSCLIMATE", "MOCLIMATE", "KYCLIMATE", "ILCLIMATE", "WICLIMATE",
 "INCLIMATE", "OHCLIMATE", "MICLIMATE"))

def get():
    ccursor.execute("""SELECT station,  min(day), max(day),
 sum(case when high > 99 THEN 1 else 0 end),
 sum(case when low < 1 THEN 1 else 0 end)
 from alldata WHERE year > 1950 and year < 2013 and
 substr(station,2,1) != 'C' and substr(station,2,4) != '0000'
 GROUP by station
 
    """)

    for row in ccursor:
        if not nt.sts.has_key(row[0]):
            continue
        if row[1].year != 1951 or row[2].year != 2012:
            continue
        print '%s,%s,%s' % (row[0], row[3], row[4])
        
lats = []
lons = []
vals = []
for line in open('tmp.txt'):
    (station, o100, u0) = line.split(",")
    o100 = float(o100)
    u0 = float(u0)
    v = o100 / u0
    if v < 1 and o100 == 0:
        v = -1000
    elif v < 1:
        v = 0 - ( u0 / o100 )
    lats.append( nt.sts[station]['lat'] )
    lons.append( nt.sts[station]['lon'] )
    vals.append( v )
    
import iemplot
cfg = {'_midwest': True,
       '_title': 'Ratio of Days with High over 100~S~o~N~F to Days with Low under 0~S~o~N~F',
       '_valid': 'stations with data between 1951 and 2012, cold colors are ratio inverse',
       'wkColorMap': 'ViBlGrWhYeOrRe',
 'cnLevelSelectionMode': 'ExplicitLevels',
 'cnLevels' : [-1000,-500,-250,-150,-100,-50,-25,-10,-5,-1,0,1,5,10,25,50,100,150,250,500,1000],
 'lbLabelStrings' : [1000,500,250,150,100,50,25,10,5,1,0,1,5,10,25,50,100,150,250,500,1000],
 'lbTitleString': 'ratio',
  'cnExplicitLabelBarLabelsOn': True,

       }
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)