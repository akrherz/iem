import matplotlib.pyplot as plt
import iemdb
import numpy as np
from scipy import stats

MESOSITE = iemdb.connect("mesosite", bypass=True)
mcursor = MESOSITE.cursor()

mcursor.execute("""
    SELECT valid, good, bad, extract(epoch from valid) from feature ORDER by valid
""")
dates = []
dates2 = []
ds = []
ds2 = []
time_of_day = []
favorable = []
for row in mcursor:
    dates.append(row[0])
    ds.append( row[3])
    if row[1] > 0:
        favorable.append( row[1] / float(row[1] + row[2])  * 100.0)
        ds2.append( row[3])
        dates2.append( row[0])
    time_of_day.append( row[0].hour * 60 + row[0].minute )
    
(fig, ax) = plt.subplots(2,1, sharex=True)

ax[0].scatter(dates, time_of_day)
ax[0].set_ylim(0, 24*60)
ax[0].set_yticks( np.arange(0,8) * 180 )
ax[0].set_yticklabels( ['Mid', '3 AM', '6 AM', '9 AM', 'Noon', '3 PM', '6 PM', '9 PM'])
ax[0].set_title("3,000 IEM Daily Features :: %s - 20 Nov 2013" % (dates[0].strftime("%-d %b %Y")))
ax[0].grid(True)
ax[0].set_ylabel("Posted Time")
h_slope, intercept, r_value, p_value, std_err = stats.linregress(ds, time_of_day)
ds = np.array(ds)
ax[0].plot(dates, h_slope * ds + intercept, lw=2, color='yellow')


ax[1].scatter(dates2, favorable)
ax[1].set_ylim(0,100)
ax[1].grid(True)
ax[1].set_ylabel("Percent of Votes as Good")
h_slope, intercept, r_value, p_value, std_err = stats.linregress(ds2, favorable)
ds3 = np.array(ds2)
ax[1].plot(dates2, h_slope * ds3 + intercept, lw=2, color='yellow')

fig.savefig('test.png')
