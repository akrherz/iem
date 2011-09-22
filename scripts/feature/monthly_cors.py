import iemdb
import numpy
import numpy.ma
import scipy.stats
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

monthlyAvgs = numpy.zeros((12,), 'd')
ccursor.execute("""
 SELECT month, sum(precip) from alldata 
 where stationid = 'ia0000' and year > 1892 GROUP by month ORDER by month ASC
""")
cnt = 0
for row in ccursor:
  monthlyAvgs[cnt] = float(row[1])
  cnt += 1

# Obs
data = numpy.zeros((2011-1893,12), 'd')
ccursor.execute("""
 SELECT year, month, sum(precip) from alldata WHERE
 stationid = 'ia0000' and year > 1892 and year < 2011 
 GROUP by year, month 
""")
for row in ccursor:
  data[row[0]-1893,row[1]-1] = float(row[2]) - monthlyAvgs[row[1]-1]

# Correlations
cors = numpy.ma.zeros((12,12))

for month1 in range(0,12):
  for month2 in range(0,12):
    if month1 == month2:
      continue
    # Okay, if month2 > month1, then we are in the same year
    if month2 > month1:
      R = numpy.corrcoef(data[:,month1], data[:,month2])[0,1]
    # Need to shift next year
    else:
      R = numpy.corrcoef(data[:-1,month1], data[1:,month2])[0,1]
    cors[month1,month2] = R 

cors.mask = numpy.where(cors==0,True,False)

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
res = ax.imshow( cors , interpolation='nearest')
fig.colorbar(res)

fig.savefig('test.png')
