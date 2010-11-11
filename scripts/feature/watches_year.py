
from matplotlib import pyplot as plt
import iemdb, numpy, iemplot
POSTGIS = iemdb.connect("postgis", bypass=True)
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
    data.append( row[1] )
  print data
  return data

#texas = numpy.array( get_data('TX') )
#iowa = numpy.array( get_data('IA') )
texas = numpy.array( [166L, 117L, 161L, 128L, 128L, 121L, 183L, 145L, 147L, 121L, 143L, 153L, 143L, 81L] , 'f')
iowa = numpy.array( [65L, 103L, 74L, 101L, 100L, 89L, 108L, 126L, 83L, 88L, 86L, 115L, 80L, 113L] , 'f')
total = numpy.array( get_total() )

fig = plt.figure()
ax = fig.add_subplot(211)
ax.bar( numpy.arange(1997,2011) - 0.33, iowa, 0.33 , color="blue", label="Iowa")
ax.bar( numpy.arange(1997,2011), texas, 0.33 , color="red", label="Texas")
ax.set_title("SPC Issued Tornado / Svr T'Storm Watches\n1 January - 15 September")
ax.set_ylabel("Number Issued")
ax.grid(True)
ax.legend(ncol=2)
ax.set_xlim(1996.5,2010.5)

ax = fig.add_subplot(212)

ax.bar( numpy.arange(1997,2011) - 0.25, iowa / total * 100., 0.5 )
ax.grid(True)
ax.set_xlim(1996.5,2010.5)
ax.set_ylabel("Percentage of Watches in Iowa")

fig.savefig("test.ps")
iemplot.makefeature("test")
