
from matplotlib import pyplot as plt
import psycopg2
import numpy
POSTGIS = psycopg2.connect(database="postgis", host="iemdb", user='nobody')
pcursor = POSTGIS.cursor()

def get_data(st):
  pcursor.execute("""select extract(year from issued) as yr, count(*) 
  from watches w, states s where w.geom && s.the_geom and 
   ST_Overlaps(w.geom, s.the_geom) and
   s.state_abbr = %s and 
   extract(doy from issued) <= extract(doy from now()) 
   GROUP by yr ORDER by yr ASC""", (st,))
  data = []
  for row in pcursor:
    data.append( row[1] )
  print data
  return data

def get_total():
  pcursor.execute("""Select extract(year from issued) as year, 
   max(num) from watches 
   where extract(doy from issued) <= extract(doy from now()) and num < 3000
   GROUP by year ORDER by year ASC""")
  data = []
  for row in pcursor:
    data.append( float(row[1]) )
  print data
  return data

#texas = numpy.array( get_data('TX') )
iowa = numpy.array( get_data('IA') )
total = numpy.array( get_total() )

fig = plt.figure()
ax = fig.add_subplot(211)
bars = ax.bar( numpy.arange(1997,2015) - 0.4, iowa, 0.8 , color="blue", label="Iowa")
for i, bar in enumerate(bars):
    ax.text(1997+i, iowa[i]+0.2, "%s" % (iowa[i],), ha='center')
bars[-1].set_facecolor('r')
#ax.bar( numpy.arange(1997,2015), texas, 0.4 , color="red", label="Texas")
ax.set_title("Storm Prediction Center Issued Tornado / Svr T'Storm Watches\n1 January - 22 April")
ax.set_ylabel("Number Issued")
ax.grid(True)
#ax.legend(ncol=2)
ax.set_xlim(1996.5,2014.5)
#ax.set_ylim(0,numpy.max(texas)+50)


ax = fig.add_subplot(212)

data = iowa / total * 100.
bars = ax.bar( numpy.arange(1997,2015) - 0.4, data, 0.8 )
for i, bar in enumerate(bars):
    ax.text(1997+i, data[i]+0.2, "%.1f%%" % (data[i],), ha='center')
bars[-1].set_facecolor('r')
ax.grid(True)
ax.set_xlim(1996.5,2014.5)
ax.set_ylabel("Watches Touching Iowa [%]")

fig.savefig("test.png")

