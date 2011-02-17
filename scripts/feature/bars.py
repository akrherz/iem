
from matplotlib import pyplot as plt
import numpy
import iemplot
import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

icursor.execute("""
select hr, dy, count(*) from (select distinct extract(hour from valid) as hr, extract(day from valid) as dy, 
station from current_log WHERE network in ('ASOS','AWOS') and
 valid > '2010-12-29' and valid < '2010-12-30 06:00' 
 and vsby <= 1) as foo GROUP by hr, dy ORDER by dy, hr ASC
""")
sites = []
#totals = []
for row in icursor:
  #years.append( row[0] )
  sites.append( row[2] )

#sixty = [2.56, 2.34, 2.18, 3.07, 2.12, 2.77]
#sixtyl = ["Spencer, 6 Apr","Esterville, 1 Aug", "Davenport, 9 Jul", "Ottumwa, 25 Jun", "Lamoni, 26 May", "Lamoni, 5 Jun"]
#onetwenty = [3.60, 2.81, 3.17, 3.15, 2.18, 3.52]
#onetwentyl = ["Spencer, 6 Apr","Esterville, 1 Aug", "Iowa City, 22 Jun", "Ottumwa, 25 Jun", "Ames, 26 May", "Ames, 31 Aug"]

fig = plt.figure()
ax = fig.add_subplot(111)

rects1 = ax.bar(numpy.arange(0,30)-0.33, sites, color='b')
#ax.plot( [1989,2011], [1.49, 1.49], color='r', label='Average 1.49')
#rects2 = ax.bar(numpy.arange(2005,2011), onetwenty, 0.33, color='r', label=('2 hour'))
#ax.set_xticklabels( numpy.arange(1990,2011) )
ax.set_xlim(-0.33, 29.66)
#ax.legend(loc=2)
ax.set_xticks( (0,6,12,18,24,30) )
ax.set_xticklabels( ('Mid\n29 Dec', '6 AM', 'Noon', '6 PM', 'Mid\n30 Dec', '6 AM'))

#for i in range(6):
#  label = "%s, %.2f" % (sixtyl[i], sixty[i])
#  ax.text( 2005 + i - 0.15, 0.05, label, color='white',
#                ha='center', va='bottom', rotation=90, fontsize=16)
#  label = "%s, %.2f" % (onetwentyl[i], onetwenty[i])
#  ax.text( 2005 + i + 0.17, 0.05, label, color='white',
#                ha='center', va='bottom', rotation=90, fontsize=16)
#

ax.set_ylabel("Airport Sites [57 total]")
ax.set_xlabel("29-30 Dec 2010")
ax.set_title("Number of ASOS/AWOS sites reporting\n 1 mile or less visibility")
ax.grid(True)
plt.savefig('test.ps')
iemplot.makefeature("test")
