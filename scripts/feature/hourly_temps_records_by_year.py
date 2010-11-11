# Compute something on the hourly temperature records, climatology perhaps
import iemdb
import datetime
import numpy
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
acursor.execute("SET TIME ZONE 'GMT'")

# Extract the climatologies
records = {}
recordset = numpy.zeros( (2011-1948,24), 'f')
for year in range(1948,2011):
    acursor.execute("""
select to_char(valid + '10 minutes'::interval, 'MMDDHH24') as mmddhh, 
max(tmpf), min(tmpf) from t%s where station = 'DSM' and 
tmpf between -50 and 120 
and (extract(minute from valid) between 50 and 59 
or extract(minute from valid) = 0) GROUP by mmddhh
    """ % (year,))
    for row in acursor:
        lkp = row[0]
        if not records.has_key(lkp):
            records[lkp] = {'max': -150, 'min': 150}
        tmpf = row[1]
        if tmpf > records[lkp]['max']:
            records[lkp]['max'] = tmpf
            recordset[year-1948,int(lkp[-2:])] += 1
            

import matplotlib.pyplot as plt

#print v


fig = plt.figure()
ax = fig.add_subplot(111)

res = ax.imshow( recordset[30:,:], aspect='auto', rasterized=True, interpolation=None,
                 )
fig.colorbar(res)

import iemplot
fig.savefig('test.png')
#iemplot.makefeature('test')
