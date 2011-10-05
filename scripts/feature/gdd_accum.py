import iemdb
import mx.DateTime
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

COOP = iemdb.connect("coop",  bypass=True)
ccursor = COOP.cursor()

def fetch(day1, day2, days):
    ccursor.execute("""
 select day, gdd50(o.high,o.low), c.gdd50 from alldata o, climate51 c 
 where c.station = o.station and o.station = 'IA0200' and 
 o.day >= '%s' and o.day < '%s' and  
 to_char(c.valid, 'mmdd') = o.sday ORDER by day ASC
 """ % (day1.strftime("%Y-%m-%d"), day2.strftime("%Y-%m-%d") ))
    diff = []
    running = 0
    for row in ccursor:
        running += (float(row[1]) - row[2])
        diff.append( running ) 
    return diff

import numpy
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

corn = [177, 165, 188, 188, 184, 181, 160, 175, 164, '???']
styles = ['g.','r.','b.','g^','r^','b^','gs','rs','bs','k']
day1 =  int(mx.DateTime.DateTime(2011,5,1).strftime("%j"))
day2 =  int(mx.DateTime.DateTime(2011,10,1).strftime("%j"))
days = day2 - day1
for yr in range(2002,2012):
  data = fetch(mx.DateTime.DateTime(yr,5,1), mx.DateTime.DateTime(yr,10,1), days)
  ax.plot(numpy.arange(day1, day1 + len(data)), data, styles[yr-2002], label=`yr`)
  ax.text( day1 + len(data) + 1, data[-1], str(corn[yr-2002]) )

ax.set_title("Ames 2002-2011 GDD Accumulated Departure\nUSDA NASS - Story County Corn Yield bu/acre")
ax.set_ylabel("GDD Accumulated Departure")
 
ax.grid(True)
ax.legend(ncol=3,loc=2, prop=prop)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(121,290)
ax.set_ylim(-305,415)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
