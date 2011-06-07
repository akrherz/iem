# Month percentile 

import sys, os, random
import iemdb
import iemplot

import mx.DateTime
now = mx.DateTime.now()

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

#pranks = []
#ccursor.execute("""
#    SELECT month, avg((high+low)/2.) from alldata where stationid = 'ia0200'
#    and year = 2010 GROUP by month ORDER by month ASC
#""")
#for row in ccursor:
#    precip = row[1]
#    ccursor2.execute("""
#    SELECT count(*) from 
#    (SELECT year, avg((high+low)/2.) as s from alldata where stationid = 'ia0200'
#    and month = %s and year < 2010 GROUP by year) as foo where s < %s
#    """, (row[0], precip))
#    row2 = ccursor2.fetchone()
#    print row[0], precip, row2[0]
#    pranks.append( row2[0] / 118.0 * 100.)

ames = [75.423728813559322, 48.305084745762713, 66.101694915254242, 66.101694915254242, 34.745762711864408, 98.305084745762713, 76.271186440677965, 99.152542372881356, 77.966101694915253, 33.898305084745758, 76.271186440677965, 38.983050847457626,
        116./118.*100.]
iowa = [72.881355932203391, 52.542372881355938, 53.389830508474581, 70.33898305084746, 53.389830508474581, 99.152542372881356, 94.915254237288138, 69.491525423728817, 58.474576271186443, 11.864406779661017, 33.050847457627121, 27.118644067796609,
        105./118.*100.]

iowaT = [13.559322033898304, 15.254237288135593, 66.949152542372886, 96.610169491525426, 61.016949152542374, 81.355932203389841, 72.033898305084747, 88.983050847457619, 41.525423728813557, 75.423728813559322, 60.169491525423723, 22.881355932203391,
         51./118.*100.]
amesT = [18.64406779661017, 14.40677966101695, 62.711864406779661, 94.067796610169495, 52.542372881355938, 70.33898305084746, 63.559322033898304, 84.745762711864401, 42.372881355932201, 64.406779661016941, 50.847457627118644, 22.033898305084744,
         57./118.*100.]


import numpy
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(211)

rects = ax.bar( numpy.arange(1,14) - 0.3, iowa, width=0.3, fc='r', label='Iowa')
rects[-1].set_facecolor('#FF969C')
rects2 = ax.bar( numpy.arange(1,14), ames, width=0.3, fc='b', label='Ames')
rects2[-1].set_facecolor('#96A3FF')

#ax.legend(loc=2)
ax.grid(True)
ax.set_yticks( (0,25,50,75,90,95,100))
ax.set_xticks( range(1,14) )
ax.set_xlim(0.6,13.6)
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec', 'Year') )
ax.set_ylabel('Precip Percentile [100=wet]')
ax.set_title("2010 Monthly Precip and Average Temps\nIEM Computed [1893-2010]")

ax = fig.add_subplot(212)

rects = ax.bar( numpy.arange(1,14) - 0.3, iowaT, width=0.3, fc='r', label='Iowa')
rects[-1].set_facecolor('#FF969C')
rects2 = ax.bar( numpy.arange(1,14), amesT, width=0.3, fc='b', label='Ames')
rects2[-1].set_facecolor('#96A3FF')

ax.legend(loc=(0.53,-0.25), ncol=2)
ax.grid(True)
ax.set_yticks( (0,25,50,75,90,95,100))
ax.set_xticks( range(1,14) )
ax.set_ylabel('Temp Percentile [100=warm]')
ax.set_xlim(0.6,13.6)
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec', 'Year') )


fig.savefig('test.ps')
iemplot.makefeature('test')
