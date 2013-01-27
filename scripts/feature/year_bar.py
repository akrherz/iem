import iemdb, numpy
COOP =iemdb.connect('postgis', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select year, count(*) from 
 (select distinct extract(year from issue) as year, eventid, phenomena, 
  wfo from warnings where phenomena in ('SV','TO') and significance = 'W' 
  and extract(doy from issue) < 17) as foo 
GROUP by year ORDER by year ASC; 
""")
years = []
precip = []
for row in ccursor:
    years.append( row[0] )
    precip.append( float(row[1]) )
    
ccursor.execute("""
select year, count(*) from 
 (select distinct extract(year from issue) as year, eventid, phenomena, 
  wfo from warnings where phenomena in ('SV','TO') and significance = 'W' 
  and extract(doy from issue) < 400) as foo 
GROUP by year ORDER by year ASC; 
""")
years2 = []
precip2 = []
for row in ccursor:
    years2.append( row[0] )
    precip2.append( float(row[1]) )

years = numpy.array(years)
years2 = numpy.array(years2)
precip = numpy.array(precip)
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

bars = ax.bar(years-0.5, precip, fc='r', ec='r', zorder=1)
ax2 = ax.twinx()
bars = ax2.bar(years2-0.1, precip2, width=0.2, fc='g', ec='g', zorder=1)
#avgV = numpy.average(precip)
#ax.plot([numpy.min(years),2013], [avgV,avgV], color='k')
#for bar in bars:
#    if bar.get_height() <= avgV:
#        bar.set_facecolor('b')
#        bar.set_edgecolor('b')

ax.set_title("US Severe T'Storm + Tornado Warnings")
ax.set_ylabel("1-16 January Total, red bar", color='r')
ax2.set_ylabel("Year Total, green bar", color='g')
ax.set_xlim(1985.5,2013.5)
ax.set_xlabel("2013 thru 16 January")
#ax.set_ylim(-35,5)
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
