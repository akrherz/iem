import matplotlib.pyplot as plt
import psycopg2
import numpy as np
from scipy import stats

MESOSITE = psycopg2.connect(database="mesosite", host='iemdb', user='nobody')
mcursor = MESOSITE.cursor()

mcursor.execute("""
    SELECT valid, good, bad, extract(epoch from valid), abstain from feature
    ORDER by valid
""")
dates = []
dates2 = []
ds = []
ds2 = []
time_of_day = []
favorable = []
abstain = []
for row in mcursor:
    dates.append(row[0])
    ds.append(row[3])
    if row[1] > 0:
        favorable.append(row[1] / float(row[1] + row[2] + row[4]) * 100.0)
        ds2.append(row[3])
        dates2.append(row[0])
        abstain.append(row[4] / float(row[1] + row[2] + row[4]) * 100.0)
    time_of_day.append(row[0].hour * 60 + row[0].minute)

(fig, ax) = plt.subplots(2, 1, sharex=True)

ax[0].scatter(dates, time_of_day)
ax[0].set_ylim(0, 24*60)
ax[0].set_yticks(np.arange(0, 8) * 180)
ax[0].set_yticklabels(['Mid', '3 AM', '6 AM', '9 AM', 'Noon', '3 PM', '6 PM',
                       '9 PM'])
ax[0].set_title(("3,500 IEM Daily Features :: %s - 27 Oct 2015"
                 ) % (dates[0].strftime("%-d %b %Y")))
ax[0].grid(True)
ax[0].set_ylabel("Posted Time")
h_slope, intercept, r_value, p_value, std_err = stats.linregress(ds,
                                                                 time_of_day)
ds = np.array(ds)
ax[0].plot(dates, h_slope * ds + intercept, lw=2, color='yellow')


ax[1].scatter(dates2, favorable, color='b', label="Good")
ax[1].scatter(dates2, abstain, color='tan', label="Abstain")
ax[1].set_ylim(0, 100)
ax[1].grid(True)
ax[1].set_ylabel("Percent of Votes")
h_slope, intercept, r_value, p_value, std_err = stats.linregress(ds2,
                                                                 favorable)
ds3 = np.array(ds2)
ax[1].plot(dates2, h_slope * ds3 + intercept, lw=2, color='yellow')

h_slope, intercept, _, _, _ = stats.linregress(ds2[-700:], favorable[-700:])
ds3 = np.array(ds2[-700:])
ax[1].plot(dates2[-700:], h_slope * ds3 + intercept, lw=2, color='red')

h_slope, intercept, _, _, _ = stats.linregress(ds2[-500:], abstain[-500:])
print h_slope, intercept
ds3 = np.array(ds2[-500:])
ax[1].plot(dates2[-500:], h_slope * ds3 + intercept, lw=2, color='red')


ax[1].legend(loc=3, ncol=2, fontsize=10)

fig.savefig('test.png')
