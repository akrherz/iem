import iemdb
import network
nt = network.Table( ("IA_COOP", "MN_COOP", 'NE_COOP', 'MO_COOP') ) 
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

icursor.execute("""
 SELECT id, count(id) as cnt, 
 min(min_tmpf) as prectot 
 from summary_2012 s JOIN stations t on (t.iemid = s.iemid) 
 WHERE day >= '2012-09-01' and day < '2012-10-08' and min_tmpf < 99
 and min_tmpf > 0 
 and t.network in ('IA_COOP', 'MN_COOP', 'NE_COOP', 'MO_COOP')
 GROUP by id ORDER by prectot ASC
""")

lats = []
lons = []
vals = []
mask = []
for row in icursor:
    #if row[1] < 25 or row[2] > 8:
    #    continue
    mask.append( row[0][-2:] == 'I4' )
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )
    vals.append( row[2] )
    
cfg = {'wkColorMap': 'WhiteBlueGreenYellowRed',
       '_showvalues': True,
       '_format': '%.2f',
       'lbTitleString': '[inch]',
       '_valuemask': mask,
       '_title' : 'September 2012 NWS COOP Rainfall Totals',
       }

import iemplot
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

iemplot.makefeature(tmpfp)
