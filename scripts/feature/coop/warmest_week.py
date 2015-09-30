import psycopg2
import datetime
import numpy as np

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

sts = datetime.datetime(2009,1,1)
ets = datetime.datetime(2010,1,1)
interval = datetime.timedelta(days=7)
now = sts

data = np.zeros( (2013-1879, 53))

i = 0
dates = []
while now < ets:
    cursor.execute("""SELECT year, avg((high+low)/2.0) from alldata_ia
    where station = 'IA2203' and sday >= '%s' and sday < '%s' 
    and year < 2013 and year > 1878 GROUP by year""" % (
        now.strftime("%m%d"), (now + interval).strftime("%m%d")))
    print now, i
    for row in cursor:
        data[row[0]-1879,i] = row[1]
    dates.append(now)
    i += 1
    now += interval

weekly_avg = np.average(data, 0)
yearly_max = np.max(data, 1)

max_week_cnt = np.zeros( (53,))

for i, val in enumerate(yearly_max):
    idx = np.argmax(data[i,:])
    max_week_cnt[idx] += 1.0
    
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(2,1)

ax[0].bar(dates[:-1], weekly_avg[:-1], width=7)
ax[0].grid(True)
ax[0].set_title("1879-2012 Des Moines Weekly Temperature Climatology")
ax[0].set_ylabel(r"Average Temperature $^\circ$F")
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax[1].bar(dates[:-1], max_week_cnt[:-1], width=7)
ax[1].grid(True)
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax[1].set_ylabel("Week was the warmest (# yrs)")
ax[1].set_xlim(min(dates),max(dates))

fig.savefig('test.png')

