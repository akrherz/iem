import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import matplotlib.pyplot as plt

ccursor.execute("""
select valid, max_high, min_high, max_low, min_low, max_precip from climate where station = 'IA0200' and valid between '2000-02-26' and '2000-03-03' ORDER by valid ASC
""")
highs = []
lows = []
precip = []
for row in ccursor:
    highs.append( row[1] )
    lows.append( row[4] )
    precip.append( row[5] )

fig = plt.figure()
ax = fig.add_subplot(211)
bars = ax.bar( numpy.arange(1,8) - 0.4 , highs  , width=0.4, facecolor='r', label='High')
bars = ax.bar( numpy.arange(1,8)  , lows  , width=0.4, facecolor='b', label='Low')
for i in range(0,7):
  ax.text( i+1-0.4, highs[i] + 1, '%.0f' % (highs[i],) )
  ax.text( i+1, lows[i] - 10, '%.0f' % (lows[i],) )
ax.set_title("Ames Daily Climatology [26 Feb - 3 Mar]")
ax.set_xlim(0,8)
ax.set_ylim(-40,90)
ax.set_ylabel('Max/Min Temp $^{\circ}\mathrm{F}$')
ax.set_xticks( numpy.arange(1,8) )
ax.set_xticklabels( ('26\nFeb', '27', '28', '29', '1\nMar','2','3'))
ax.grid(True)
#ax.legend()

ax = fig.add_subplot(212)
bars = ax.bar( numpy.arange(1,8) - 0.4 , precip, facecolor='g')
for i in range(0,7):
  ax.text( i+1-0.2, precip[i] + 0.1, '%.2f' % (precip[i],) )

ax.set_ylabel('Max Precip [inch]')
ax.set_xlim(0, 8)
ax.set_ylim(0,2)
ax.set_xticks( numpy.arange(1,8) )
ax.set_xticklabels( ('26\nFeb', '27', '28', '29', '1\nMar','2','3'))
ax.grid(True)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
