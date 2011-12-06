
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

texas = numpy.array( [179L, 133L, 166L, 151L, 148L, 137L, 186L, 152L, 163L, 144L, 151L, 159L, 163L, 93L, 111L] , 'f')
iowa = numpy.array( [72L, 108L, 74L, 105L, 110L, 93L, 109L, 131L, 96L, 98L, 93L, 117L, 80L, 121L, 83L] , 'f')
total = numpy.array(  [791, 897, 709, 803, 810, 768, 946, 877, 872, 863, 733, 933, 786, 739, 886] , 'f')
#total = numpy.array( get_total() )

fig = plt.figure()
ax = fig.add_subplot(211)
ax.bar( numpy.arange(1997,2012) - 0.33, iowa, 0.33 , color="blue", label="Iowa")
ax.bar( numpy.arange(1997,2012), texas, 0.33 , color="red", label="Texas")
ax.set_title("SPC Issued Tornado / Svr T'Storm Watches\n1 January - 15 November")
ax.set_ylabel("Number Issued")
ax.grid(True)
ax.legend(ncol=2)
ax.set_xlim(1996.5,2011.5)
ax.set_ylim(0,numpy.max(texas)+50)


ax = fig.add_subplot(212)

ax.bar( numpy.arange(1997,2012) - 0.25, iowa / total * 100., 0.5 )
ax.grid(True)
ax.set_xlim(1996.5,2011.5)
ax.set_ylabel("Percentage of Watches in Iowa")

fig.savefig("test.ps")
iemplot.makefeature("test")
