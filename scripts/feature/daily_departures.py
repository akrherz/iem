import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 select day, o.high, o.high - c.high as d from alldata_ia o JOIN climate c 
 on (c.station = o.station and o.sday = to_char(c.valid, 'mmdd')) 
 WHERE year = 2012 and o.station = 'IA2203' and o.high > 79 ORDER by day ASC
""")
jdays = []
departures = []

for row in ccursor:
    jdays.append( int(row[0].strftime("%j")))
    departures.append( row[2] )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2,1)

bars = ax[0].bar(jdays, departures, fc='b', ec='b')
for bar in bars:
    if bar.get_y() == 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax[0].set_xticks( (1,32,60,91,121,152,182,213,244,274,305) )
ax[0].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct') )
ax[0].grid(True)
ax[0].set_xlim(0,300)
ax[0].set_ylabel("Temperature Departure $^{\circ}\mathrm{F}$")
ax[0].set_title("Des Moines Daily High Temperature Departure\nfor 2012 (thru 21 Oct) on days with high over 80$^{\circ}\mathrm{F}$")

ccursor.execute("""
 select year, sum(case when d > 10 then 1 else 0 end) / count(*)::numeric as dd 
 from (select year, o.high, o.high - c.high as d from alldata_ia o 
 JOIN climate c on (c.station = o.station and o.sday = to_char(c.valid, 'mmdd')) 
 WHERE o.station = 'IA2203' and o.high > 79) as foo GROUP by year ORDER by year
""")
years = []
ratio = []
for row in ccursor:
    years.append( row[0] )
    ratio.append( float(row[1]) * 100.0)
    
bars = ax[1].bar(years, ratio, fc='r', ec='r')
for bar in bars:
    if bar.get_height() >= 50:
        bar.set_facecolor('g')
        bar.set_edgecolor('g')

ax[1].set_xlim(1880,2013)
ax[1].set_ylabel("Percentage [%]")
ax[1].set_title("Percentage of Days with 10+$^{\circ}\mathrm{F}$ Departure")
ax[1].grid(True)
    

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')