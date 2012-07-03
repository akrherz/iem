import iemdb
COOP = iemdb.connect('asos', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()
import network
nt = network.Table(('IA_ASOS','MO_ASOS','IL_ASOS',
         'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS', 'AWOS',
         'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS'))


ccursor.execute("""
 SELECT distinct date(valid) from alldata where station = 'DSM' and tmpf >= 100
 ORDER by date ASC
""")
stcnts = {}
sthits = {}
for row in ccursor:
    print row
    ccursor2.execute("""
    SELECT station, max(tmpf) from t%s WHERE valid BETWEEN '%s 00:00' and
    '%s 23:59' and station in %s GROUP by station
    """ % (row[0].year, row[0], row[0], tuple(nt.sts.keys())))
    for row2 in ccursor2:
        station = row2[0]
        if not stcnts.has_key(station):
            stcnts[station] = 0
            sthits[station] = 0
        stcnts[station] += 1
        if row2[1] >= 100:
            sthits[station] += 1
        
vals = []
lats = []
lons = []
for station in sthits.keys():
    if stcnts[station] < 10:
        continue
    vals.append( float(sthits[station]) / float(stcnts[station]) * 100.0)
    lats.append( nt.sts[station]['lat'] )
    lons.append( nt.sts[station]['lon'] )

import iemplot
cfg = {'lbTitleString': '%',
       '_showvalues': True,
       '_midwest': True,
       '_format': '%.1f'}
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)