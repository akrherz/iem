import psycopg2
import numpy
import datetime
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

obs = [0]*91
running91 = [0]*91
minyear = numpy.zeros((2017-1893), 'f')
minyear[:] = 10000.0
mindoy = numpy.zeros((2017-1893), 'f')

maxyear = numpy.zeros((2017-1893), 'f')
maxyear[:] = 0.0
maxdoy = numpy.zeros((2017-1893), 'f')

running = []
dates = []

ccursor.execute("""SELECT day, (high+low)/2.0,
extract(doy from day) from alldata_ia WHERE
  station = 'IA0200' and day >= '1893-01-01' ORDER by day ASC""")
for row in ccursor:
    obs.append(float(row[1]))
    obs.pop(0)
    year = row[0].year
    avg = sum(obs) / 91.0
    if avg < minyear[year-1893]:
        minyear[year-1893] = avg
        mindoy[year-1893] = int(row[2])

    if avg > maxyear[year-1893]:
        maxyear[year-1893] = avg
        maxdoy[year-1893] = int(row[2])

    if row[0].year >= 2014:
        running.append( avg )
        dates.append( row[0] ) 


(fig, ax) = plt.subplots(3, 1, figsize=(8, 9))

ax[0].plot(dates, running)
ax[0].set_title("1894-2016 Ames 91 Day Average Temperatures")
ax[0].set_ylabel("Trailing 91 Day Avg T $^{\circ}\mathrm{F}$")
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax[0].grid(True)

for yr in range(2014, 2017):
    doy = mindoy[yr-1893]
    val = minyear[yr-1893]
    ts = datetime.datetime(yr, 1, 1) + datetime.timedelta(days=(doy-1))
    ax[0].text(ts, val - 5,
               "%s %.1f$^\circ$F" % (ts.strftime("%-d %b"),
                                     val), ha='center')

for yr in range(2014, 2016):
    doy = maxdoy[yr-1893]
    val = maxyear[yr-1893]
    ts = datetime.datetime(yr, 1, 1) + datetime.timedelta(days=(doy-1))
    ax[0].text(ts, val + 1, '%s' % (ts.strftime("%-d %b"),), ha='center')


h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(numpy.arange(1894,2017), 
                                                                   mindoy[1:])
ax[1].scatter(numpy.arange(1894, 2017), mindoy[1:])
ax[1].grid(True)
ax[1].set_yticks([15, 32, 47, 61, 76, 93])
ax[1].set_yticklabels(['15 Jan','1 Feb', '15 Feb', '1 Mar', '15 Mar', '1 Apr'])
ax[1].set_ylabel("Date of Minimum (Spring Start)")
ax[1].set_xlim(1894, 2017)
avgv = numpy.average(mindoy[1:])
ax[1].axhline(avgv, color='r')
ax[1].plot([1894, 2013], [intercept + (1894 * h_slope), intercept + (2013 * h_slope)])
d = (datetime.date(2000, 1, 1) +
     datetime.timedelta(days=int(avgv))).strftime("%-d %b")
ax[1].text(0.02, 0.02,
           r"$\frac{\Delta days}{decade} = %.2f,R^2=%.2f, avg = %s$" % (
                h_slope * 10.0, h_r_value ** 2, d), va='bottom',
           transform=ax[1].transAxes)
ax[1].set_ylim(bottom=(ax[1].get_ylim()[0] - 10))

h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(numpy.arange(1894,2016), maxdoy[1:-1] - mindoy[1:-1] - 91)
ax[2].scatter(numpy.arange(1894, 2016), maxdoy[1:-1] - mindoy[1:-1] - 91)
ax[2].set_xlim(1894, 2017)
ax[2].set_ylabel("Length of 'Spring' [days]")
ax[2].grid(True)
avgv = numpy.average(maxdoy[1:-1] - mindoy[1:-1] - 91)
ax[2].axhline(avgv, color='r')
ax[2].plot([1894,2013], [intercept + (1894 * h_slope), intercept + (2013 * h_slope)])
ax[2].text(0.02, 0.02,
           r"$\frac{\Delta days}{decade} = %.2f,R^2=%.2f, avg = %.1fd$" % (
                h_slope * 10.0, h_r_value ** 2, avgv),
           va='bottom', transform=ax[2].transAxes)
ax[2].set_ylim(bottom=(ax[2].get_ylim()[0] - 15))

fig.savefig('test.png')
