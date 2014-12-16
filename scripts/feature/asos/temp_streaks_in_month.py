import psycopg2
pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = pgconn.cursor()
import datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pytz

(fig, ax) = plt.subplots(1,1)

interval = datetime.timedelta(days=1,hours=12)
def plot(valid, tmpf, year):
    if len(valid) == 0:
        return
    if (valid[-1] - valid[0]) > interval:
        print year, valid[-1], valid[-1] - valid[0]
        line = ax.plot(valid, tmpf, lw=2)
        delta = (valid[-1] - valid[0]).days * 86400. + (valid[-1] - valid[0]).seconds
        i = tmpf.index(min(tmpf))
        ax.text(valid[i], tmpf[i], "%s\n%.1fd" % (year, delta / 86400.), 
                ha='center', va='top',
                bbox=dict(color=line[0].get_color()),
                color='white')
    

cursor.execute("""
  SELECT valid, tmpf from alldata where station = 'DSM'
  and tmpf is not null and extract(month from valid) = 12
  ORDER by valid ASC
  """)

valid = []
tmpf = []
year = 0
for row in cursor:
    if year != row[0].year:
        year = row[0].year
        plot(valid, tmpf, year)
        valid = []
        tmpf = []
    if row[1] > 49.5:
        valid.append(row[0].replace(year=2000))
        tmpf.append(row[1])
    if row[1] < 49.5:
        valid.append(row[0].replace(year=2000))
        tmpf.append(row[1])
        plot(valid, tmpf, year)
        valid = []
        tmpf = [] 

plot(valid, tmpf, year)

ax.set_xlim(datetime.datetime(2000,12,1), datetime.datetime(2001,1,1))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=2,
                                              tz=pytz.timezone("America/Chicago")))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d'))
ax.grid(True)
ax.set_ylabel("Temperature $^\circ$F")
ax.set_xlabel("Day of December")
ax.set_title("1929-2014 Des Moines Airport 1.5+ Day Streaks Above 50$^\circ$F")
#ax.axhline(32, linestyle='-.', linewidth=2, color='k')
ax.set_ylim(bottom=43)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
