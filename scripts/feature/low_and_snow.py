import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT low, sum(case when snowd > 0 then 1 else 0 end) / count(*):: numeric,
 count(*) from alldata_ia where station = 'IA2203' and low < 32 
 and year > 1899 and snowd >= 0 and year < 2012 GROUP by low ORDER by low DESC
""")
lows = []
freq = []
count = []
for row in ccursor:
    lows.append( row[0] )
    freq.append( float(row[1]) * 100.0 )
    count.append( float(row[2]) / 111.0 )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.plot(lows, freq, color='b')

ax2 = ax.twinx()

ax2.plot(lows, count, color='r')

ax.set_xlim(32, -30)
ax.set_title("1900-2011 Des Moines Daily Low Temperature + Snow Cover")
ax.set_ylabel("Frequency of Snow Cover [%]", color='b')
ax2.set_ylabel("Frequency of Low Temp per Year", color='r')
ax.set_xlabel("Daily Low Temperature $^{\circ}\mathrm{F}$")
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')