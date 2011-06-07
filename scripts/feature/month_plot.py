# Lets run some diagnostics on blizzard criterion

import pylab
import iemdb, network, iemplot
import numpy
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
st = network.Table( ('IA_ASOS', 'AWOS') )

    
icursor.execute("""
select may.station, may.min - april.min as diff from (select station, min(min_tmpf) from summary_2011 where extract(month from day) = 5 and (network = 'IA_ASOS' or network = 'AWOS') and min_tmpf < 80 GROUP by station) as may, (select station, min(min_tmpf) from summary_2011 where extract(month from day) = 4 and (network = 'IA_ASOS' or network = 'AWOS') and min_tmpf < 80 GROUP by station) as april WHERE april.station = may.station ORDER by diff
    """, (id,))
diff = []
lats = []
lons = []
for row in icursor:
  if row[0] == 'HNR':
    continue
  lats.append( st.sts[row[0]]['lat'] )
  lons.append( st.sts[row[0]]['lon'] )
  diff.append( row[1] )

cfg = {
 '_title' : '2011 May versus April Minimum Temperature',
 '_valid' : 'Through 4 May',
 '_format' : '%.0f',
}
tmp = iemplot.simple_valplot(lons, lats, diff, cfg)
#iemplot.postprocess(tmp,'','')

import iemplot
iemplot.makefeature(tmp)
