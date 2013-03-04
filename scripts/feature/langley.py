"""

 one langley is 41840.00 J/m2(or joules per square metre).
 one Langley is 11.622 watt-hours per square metre

 400 W/m2 1440 000 J/hr

"""
import iemdb
ISUAG = iemdb.connect('isuag', bypass=True)
icursor = ISUAG.cursor()

icursor.execute("""
 select valid, c80
 from daily WHERE station = 'A130209' and valid > '2012-11-01'
 ORDER by valid ASC 
""")

obs = []
days = []
for row in icursor:
 days.append( row[0] )
 obs.append( row[1] )

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(1,1)

ax.bar(days, obs, fc='pink', ec='pink')
ax.grid(True)
ax.set_title("ISUAG Ames Daily Solar Radiation")
ax.set_ylabel("Solar Radiation [Langleys per day]")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y'))

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
