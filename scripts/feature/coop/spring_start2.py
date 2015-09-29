import iemdb
import numpy
import datetime
from scipy import stats

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

obs = [0]*91
running91 = [0]*91
minyear = numpy.zeros((2014-1893), 'f')
minyear[:] = 10000.0
mindoy = numpy.zeros((2014-1893), 'f')

maxyear = numpy.zeros((2014-1893), 'f')
maxyear[:] = 0.0
maxdoy = numpy.zeros((2014-1893), 'f')

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


    if row[0].year >= 2009:
        running.append( avg )
        dates.append( row[0] ) 
        
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(3,1, figsize=(7,10))

ax[0].plot(dates, running)
ax[0].set_title("1894-2013 Ames 91 Day Average Temperatures")
ax[0].set_ylabel("Trailing 91 Day Avg T $^{\circ}\mathrm{F}$")
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))

for yr in range(2009,2014):
    doy = mindoy[yr-1893]
    val = minyear[yr-1893]
    ts  = datetime.datetime(yr,1,1) + datetime.timedelta(days=(doy-1))
    ax[0].text(ts, val - 5, '%s' % (ts.strftime("%-d %b"),), ha='center')

for yr in range(2009,2013):
    doy = maxdoy[yr-1893]
    val = maxyear[yr-1893]
    ts  = datetime.datetime(yr,1,1) + datetime.timedelta(days=(doy-1))
    ax[0].text(ts, val +1, '%s' % (ts.strftime("%-d %b"),), ha='center')


h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(numpy.arange(1894,2014), 
                                                                   mindoy[1:])
ax[1].scatter(numpy.arange(1894,2014), mindoy[1:])
ax[1].grid(True)
ax[1].set_yticks([15,32,47,61,76,93])
ax[1].set_yticklabels(['15 Jan','1 Feb', '15 Feb', '1 Mar', '15 Mar', '1 Apr'])
ax[1].set_ylabel("Date of Minimum (Spring Start)")
ax[1].set_xlim(1894,2014)
ax[1].plot([1894,2013], [intercept + (1894 * h_slope), intercept + (2013 * h_slope)])
ax[1].text(1900, 25, r"$\frac{\Delta days}{decade} = %.2f,R^2=%.2f$" % (
                h_slope * 10.0, h_r_value ** 2), va='bottom')

h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(numpy.arange(1894,2013), maxdoy[1:-1] - mindoy[1:-1] - 91)
ax[2].scatter(numpy.arange(1894,2013), maxdoy[1:-1] - mindoy[1:-1] - 91)
ax[2].set_xlim(1894,2014)
ax[2].set_ylabel("Length of 'Spring' [days]")
ax[2].grid(True)
ax[2].plot([1894,2013], [intercept + (1894 * h_slope), intercept + (2013 * h_slope)])
ax[2].text(1900, 61, r"$\frac{\Delta days}{decade} = %.2f,R^2=%.2f$" % (
                h_slope * 10.0, h_r_value ** 2), va='bottom')

fig.savefig('test.png')
