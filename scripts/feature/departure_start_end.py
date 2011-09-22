import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

may1sep1 = 11.16
may1oct1 = 4.1
diff = may1oct1 - may1sep1 

ccursor.execute("""
  select year, sum(case when month in (7,8,9) then precip else 0 end),
  sum(case when month in (10,11) then precip else 0 end) from alldata
  WHERE year < 2011 and stationid = 'ia0000' GROUP by year ORDER by year ASC
""")

sep1 = []
oct1 = []
belowcnt = 0
abovecnt = 0
for row in ccursor:
  sep1.append( row[1] - may1sep1 )
  oct1.append( row[2] - may1oct1 )
  if ( row[1] - may1sep1 ) < 0:
    belowcnt += 1
    if ( row[2] - may1oct1 ) > 0:
      abovecnt += 1

import matplotlib.pyplot as plt
fig = plt.figure()
ax= fig.add_subplot(111)

ax.scatter( sep1, oct1 )
ax.plot([-15,25],[-15,25], label="Avg Sept")
ax.plot([-15+diff,25+diff],[-15,25], color='r', label="Dry Sept")
ax.plot([-1,-1],[-15,25], color='g', label="2011")
ax.text(-14.5,5.5, "Below @Sep 1: %s\nAbove @Oct 1: %s %.1f%%" % (belowcnt, abovecnt, float(abovecnt) / float(belowcnt) * 100.)) 
ax.grid(True)
ax.set_xlabel("1 May - 1 September Depature [inch]")
ax.set_ylabel("1 May - 1 October Depature [inch]")
ax.set_title("Making up State Precipitation Depatures in September")
ax.legend(loc=4)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
