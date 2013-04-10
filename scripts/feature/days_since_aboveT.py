
import pg
import datetime
import iemdb
import network

now = datetime.date(2013,3,26)

nt = network.Table('IACLIMATE')
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
lats = []
lons = []
vals = []
#"""
for sid in nt.sts.keys():
    if sid[2] == 'C' or sid == 'IA0000':
        continue
    ccursor.execute("""SELECT o.station, day from alldata_ia o, climate81 c WHERE
      c.station = %s and c.station = o.station and 
      o.sday = to_char(c.valid, 'mmdd') and o.day > '2012-01-01'
      and o.high > c.high ORDER by day DESC LIMIT 1""" , (sid,) )
    row = ccursor.fetchone()
    if row is None:
        continue
    print sid, row[1]
    lats.append( nt.sts[sid]['lat'] )
    lons.append( nt.sts[sid]['lon'] )
    vals.append( (now - row[1]).days )
    
#"""

#lons[ vals.index(707) ] += 0.09
#lats[ vals.index(707) ] -= 0.09

import iemplot
cfg = {
 '_title' : 'Days Since Daily High Temperature above Average',
 '_valid' : '26 March 2013 against 1981-2010 Climatology',
 '_showvalues' : True,
 '_format' : '%.0f',
 'lbTitleString' : 'Days'
}
fp = iemplot.simple_valplot(lons, lats, vals, cfg)
#iemplot.postprocess( fp , "")
iemplot.makefeature( fp )
