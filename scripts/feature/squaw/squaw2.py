""" Accumulate PET for this year and previous ones """
import iemdb
ISUAG = iemdb.connect('squaw', bypass=True)
icursor = ISUAG.cursor()
import numpy.ma
import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
(fig, ax) = plt.subplots(1, 1)

icursor.execute("""SELECT date(valid) as d, max(cfs) from real_flow
    WHERE valid > '2010-01-01'
    GROUP by d ORDER by d ASC""")
vals = []
days = []
for row in icursor:
    days.append( row[0] )
    vals.append( row[1] )
    
ax.plot(days, vals, lw=2)

ax.set_title("Ames Squaw Creek at Lincoln Way")
ax.set_xlabel("1 June 2010 thru 11 March 2013")
ax.set_ylabel("Water Flow [cfs], log scale")
#ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
#ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(datetime.date(2010,6,1), datetime.date(2013,4,1))
ax.set_yscale('log')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax.grid(True)
fig.savefig('test.png')
