import mesonet
import iemdb
ASOS = iemdb.connect('iem', bypass=True)
acursor = ASOS.cursor()
import mx.DateTime
import numpy
import network
nt = network.Table(("IA_ASOS", 'AWOS'))

acursor.execute("""SELECT t.id, valid, tmpf, dwpf from current_log c JOIN stations t on
    (t.iemid = c.iemid) WHERE t.network in ('IA_ASOS','AWOS') and valid 
    BETWEEN '2012-09-04' and '2012-09-05'
    and tmpf > 0 and dwpf > 0 """)

maxes = {}
for row in acursor:
    h = mesonet.heatidx(row[2], mesonet.relh(row[2], row[3]))
    maxes[row[0]] = max(h, maxes.get(row[0], 0))

vals = []
lons = []
lats = []
for sid in maxes.keys():
    vals.append( maxes[sid])
    lons.append( nt.sts[sid]['lon'] )
    lats.append( nt.sts[sid]['lat'] )
    
cfg = {'wkColorMap': 'WhiteYellowOrangeRed',
       '_title': '4 Sep 2012 ASOS/AWOS Maximum Heat Index',
       'lbTitleString': 'F',
       '_showvalues': True,
       '_format': '%.0f'
       }
import iemplot
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)
