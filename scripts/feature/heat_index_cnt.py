import mesonet
import iemdb
ASOS = iemdb.connect('iem', bypass=True)
acursor = ASOS.cursor()
import mx.DateTime
import numpy
import network
from pyiem.plot import MapPlot
nt = network.Table(('IA_ASOS','MO_ASOS','IL_ASOS', 'ND_ASOS', 'AWOS',
          'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS',
          'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS'))

acursor.execute("""SELECT t.id, valid, tmpf, dwpf from current_log c JOIN stations t on
    (t.iemid = c.iemid) WHERE t.network in ('IA_ASOS','MO_ASOS','IL_ASOS', 'ND_ASOS', 'AWOS',
          'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS',
          'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS') and valid 
    BETWEEN '2014-07-21' and '2014-07-22'
    and tmpf > 0 and dwpf > 0 """)

maxes = {}
for row in acursor:
    h = mesonet.heatidx(row[2], mesonet.relh(row[2], row[3]))
    maxes[row[0]] = max(h, maxes.get(row[0], 0))

vals = []
lons = []
lats = []
for sid in maxes.keys():
    if not nt.sts.has_key(sid) or maxes[sid] > 120:
        continue
    vals.append( maxes[sid])
    lons.append( nt.sts[sid]['lon'] )
    lats.append( nt.sts[sid]['lat'] )

m = MapPlot('midwest',
   title='21-22 July 2014 Peak Heat Index',
   subtitle='based on hourly observations')
m.contourf(lons, lats, vals, numpy.arange(80,121,5))
m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')
