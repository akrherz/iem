import iemdb
import network
nt = network.Table( ("IA_COOP", "MN_COOP", 'NE_COOP', 'MO_COOP') ) 
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

icursor.execute("""
 SELECT id, count(id) as cnt, 
 sum(CASE WHEN pday >= 0 THEN pday ELSE 0 END) as prectot 
 from summary_2012 s JOIN stations t on (t.iemid = s.iemid) 
 WHERE day >= '2012-05-01' and day < '2012-08-01' 
 and pday >= 0 and t.network in ('IA_COOP', 'MN_COOP', 'NE_COOP', 'MO_COOP')
 GROUP by id ORDER by prectot ASC
""")

lats = []
lons = []
vals = []
mask = []
for row in icursor:
    if row[1] < 80:
        continue
    mask.append( row[0][-2:] == 'I4' )
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )
    vals.append( row[2] )
    
cfg = {'wkColorMap': 'WhiteBlueGreenYellowRed',
       '_showvalues': True,
       '_format': '%.2f',
       'lbTitleString': '[inch]',
       '_valuemask': mask,
       '_title' : 'May-July 2012 NWS COOP Rainfall Totals',
       }

import iemplot
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

iemplot.makefeature(tmpfp)