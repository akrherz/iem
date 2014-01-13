import iemdb
import random
ASOS = iemdb.connect('iem', bypass=True)
icursor = ASOS.cursor()
import iemplot

icursor.execute(""" 
 WITH data as 
 (SELECT iemid,  min(wcht(tmpf::numeric, (sknt*1.15)::numeric)) from current_log WHERE tmpf > -50 and sknt >= 0 GROUP by iemid)

 SELECT ST_x(geom), ST_y(geom), d.min, t.network, t.id from data d JOIN stations t 
 ON (t.iemid = d.iemid)
 WHERE t.state in ('IA','MN','WI','ND','SD','NE','KS','MO','IL','IN','MI','OH','KY') and (t.network = 'AWOS' or t.network ~* 'ASOS')
 and t.id not in ('DKB', 'M30', 'CIR', 'EKQ', 'SME', 'P58')
 ORDER by d.min ASC
 """)
lats = []
lons = []
data = []
for row in icursor:
    print '%s %s %.1f' % (row[3], row[4], row[2])
    data.append( row[2] )
    lats.append( row[1] + (random.random()*0.001))
    lons.append( row[0] )
    
cfg = {
       '_midwest': True,
       'lbTitleString': '[F]',
       '_title': '5-6 January 2014 Minimum Wind Chill',
       #'_showvalues': True,
       #'_format': '%.0f',
       }

fp = iemplot.simple_contour(lons, lats, data, cfg)
#iemplot.postprocess(fp,'','')
iemplot.makefeature(fp)
