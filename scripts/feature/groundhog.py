import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import numpy
shadow = numpy.zeros( (2011-1950), 'f')
data = numpy.zeros( (2011-1950), 'f')

for yr in range(1950,2011):
    # Look out our ASOS data
    acursor.execute("""
    SELECT skyc1, skyc2, skyc3, skyc4 from t%s WHERE station = 'DSM'
    and valid BETWEEN '%s-02-02 08:00' and '%s-02-02 09:15'
    """ % (yr, yr, yr))
    row = acursor.fetchone()
    if row is None:
        print "MISSING", yr
     
    # Load up 6 week data
    ccursor.execute("""
    SELECT max(extract(doy from day)) from alldata WHERE
    stationid = 'ia2203' and day > '%s-02-02' and
    day < ('%s-02-02'::date + '14 weeks'::interval)
    and snow > 0 
    """ % (yr,yr))
    row2 = ccursor.fetchone()
    
    data[yr-1950] = row2[0] 
    if row is None or row[0] is None or row[0] in ('SCT','CLR'):
        shadow[yr-1950] = 1. 
    else:
        shadow[yr-1950] = 0. 

import matplotlib.pyplot as plt
import numpy 

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter( shadow, data )
ax.set_xlim(-1,10)
fig.savefig('test.png')