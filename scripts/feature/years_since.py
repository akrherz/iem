import numpy
import pg
import mx.DateTime

conn = pg.connect("coop", "iemdb", user="nobody")

rs = conn.query("select high, sday from alldata_ia where stationid = 'ia2203' and day > '2010-12-31' ORDER by sday ASC").dictresult()

years = []
for row in rs:
    rs2 = conn.query("SELECT max(year) from alldata_ia WHERE stationid = 'ia2203' and sday = '%s' and high >= %s and year < 2011" % (row['sday'], row['high'])).dictresult()
    if rs2[0]['max'] is None:
        rs2[0]['max'] = 1893
    years.append( 0 - (2011 - rs2[0]['max']) )
# 0901
years.append( -27 )

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import iemplot

fig = plt.figure()
ax = fig.add_subplot(111)
rects = ax.bar( np.arange(1,1+len(years))-0.4, years, color='r', edgecolor='r')
#ax.set_ylim(0,50)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(1,245)
ax.grid(True)
#ax.legend()
ax.set_ylabel("Last year of as warm high")
ax.set_title("2011 Des Moines Daily High Temperature")
ax.set_ylim(0,-110)
ax.set_yticks( numpy.arange(1,-131,-10) )
ax.set_yticklabels( numpy.arange(2010,1880,-10) )
#ax.set_yticklabels( ('120', '100', '80', '60', '40', '20', '0') )
#ax.text(1941, 22, "Max High Temperature")



fig.savefig("test.ps")
iemplot.makefeature("test")
