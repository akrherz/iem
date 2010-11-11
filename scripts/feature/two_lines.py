
import matplotlib.pyplot as plt
import iemdb
import numpy
dbconn = iemdb.connect("coop", bypass=True)

a1993 = []
a2010 = []
climate = []
c = dbconn.cursor()
c.execute("""SELECT valid, precip from climate51 where station = 'ia2203'
          and valid >= '2000-06-01' and valid < '2000-09-01' ORDER by valid ASC""")
running = 0
for row in c:
  running += row[1]
  climate.append( running )
climate = numpy.array( climate )

c.execute("""SELECT day, precip from alldata where stationid = 'ia2203'
          and month in (6,7,8) and year = 2010 ORDER by day ASC""")
running = 0
for row in c:
  running += row[1]
  a2010.append( running )
#a2010.append(running + 1.17)
a2010 = numpy.array( a2010 )
c.execute("""SELECT day, precip from alldata where stationid = 'ia2203'
          and month in (6,7,8) and year = 1993 ORDER by day ASC""")
running = 0
for row in c:
  running += row[1]
  a1993.append( running )
a1993 = numpy.array( a1993 )
c.close()
dbconn.close()

def modcolor(rects):
  for rect in rects:
    if rect.get_y() >= 0:
      rect.set_facecolor('b')
    else:
      rect.set_facecolor('r')


fig = plt.figure()
ax = fig.add_subplot(211)

ln1 = ax.plot( numpy.arange(0,92), a2010, color='r')
ln2 = ax.plot( numpy.arange(0,92), a1993, color='b')
ln3 = ax.plot( numpy.arange(0,92), climate, color='g')

ax.set_xticks( (0, 30, 61) )
ax.set_xticklabels( ('Jun 1', 'Jul 1', 'Aug 1') )

ax.legend( (ln1, ln2,ln3), ('2010 %.2f' % (a2010[-1],), '1993 %s' % (a1993[-1],), 'Climatology') , loc=2)
ax.grid(True)
ax.set_ylabel("Accumulated Precip [inch]")
ax.set_title("The race for wettest summer\nDes Moines (Jun/Jul/Aug)")
ax.set_xlim(0,92)

ax = fig.add_subplot(212)
rects = ax.bar( numpy.arange(0,92), a2010 - a1993 )
modcolor( rects )
ax.grid(True)
ax.set_ylabel("2010 minus 1993")
ax.set_xticks( (0, 30, 61) )
ax.set_xticklabels( ('Jun 1', 'Jul 1', 'Aug 1') )
ax.set_xlim(0,92)

plt.savefig('test.ps')
