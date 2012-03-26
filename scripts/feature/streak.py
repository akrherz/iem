import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

obs = numpy.zeros( (2013-1893,31), 'f')

ccursor.execute("""SELECT day, high 
    from alldata where station = 'IA0200' and month = 3
    and year > 1892""")
for row in ccursor:
    obs[row[0].year-1893,row[0].day-1] = row[1]


minT = numpy.zeros( (31,), 'f')
lbl = [""]*31
for yr in range(1893,2013):
  for dinterval in range(1,32):
    for dom in range(1,32-dinterval+1):
       mv = numpy.min( obs[yr-1893,(dom-1):(dom+dinterval-1)] )
       if mv > minT[dinterval-1]:
           #print dy, yr, mv
           minT[dinterval-1] = mv
           lbl[dinterval-1] = "%s-%s %s" % (dom,dom+dinterval-1,yr,)


import matplotlib.pyplot as plt
import matplotlib.font_manager
import numpy
prop = matplotlib.font_manager.FontProperties(size=10) 
fig = plt.figure()
ax = fig.add_subplot(111)
bars = ax.bar(numpy.arange(1,32)-0.4, minT, fc='lightblue')
for i in range(1,32):
  ax.text(i-0.3, minT[i-1]-2, lbl[i-1], rotation=90, va='top',fontproperties=prop)
ax.grid(True)
ax.set_xlabel("Number of Days in March, ties not shown")
ax.set_ylabel("Minimum High Temperature $^{\circ}\mathrm{F}$")
ax.set_title("Maximum of Minimum High Temperature over a period in March\nAmes (1893-2011)")
ax.set_xlim(0,32)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')   
