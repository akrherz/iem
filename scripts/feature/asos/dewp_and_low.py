import psycopg2
import numpy as np
import datetime

dwpf = [0]*53
lowt = [0]*53
hits = [0]*53
hits2 = [0]*53
for i in range(53):
    dwpf[i] = []
    lowt[i] = []
    hits[i] = []
    hits2[i] = []

ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()


acursor.execute("""
  SELECT afternoon.date, afternoon.avg, morning.min from
  (SELECT date(valid + '1 day'::interval), avg(dwpf) from alldata where
  station = 'DSM' and extract(hour from valid + '10 minutes'::interval) = 16
  and extract(minute from valid + '10 minutes'::interval) <= 10 and dwpf > -30
  GROUP by date) as afternoon,
  (SELECT date(valid), min(tmpf) from alldata where
  station = 'DSM' and extract(hour from valid + '10 minutes'::interval) 
  between 1 and 11 and tmpf > -30 GROUP by date) as morning
  WHERE morning.date = afternoon.date
""")

for row in acursor:
    doy = int(row[0].strftime("%U")) - 1
    dwpf[doy].append( row[1] )
    lowt[doy].append( row[2] )
    a = 0
    if abs( row[1] - row[2] ) <= 3:
        a = 1
    hits[doy].append( a )
    a = 0
    if row[2] < row[1]: # low temp less than 4 pm dew point
        a = 1
    hits2[doy].append( a )
    
corr = []
ratio = []
ratio2 = []
bias = []
x = []
for i in range(53):
    x.append( datetime.datetime(2000,1,1) + datetime.timedelta(days=i*7))
    c = np.corrcoef(dwpf[i], lowt[i])[0,1]
    corr.append( c )
    ratio.append( sum(hits[i]) / float(len(hits[i])) * 100.0)
    ratio2.append( sum(hits2[i]) / float(len(hits2[i])) * 100.0)
    bias.append( (sum(dwpf[i]) - sum(lowt[i])) / float(len(lowt[i])) )
    print i, c
    
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(3,1, sharex=True)

ax[0].set_title("1935-2013 Des Moines 4 PM Dew Point vs Next Morning Low")

ax[0].bar(x, ratio, width=7, fc='b', ec='b')
ax[0].set_ylabel("Dewpoint within\n3$^\circ$F of low [%]")
ax[0].grid(True)

ax[1].bar(x, ratio2, width=7, fc='b', ec='b')
ax[1].set_ylabel("Low Temp Colder\nthan Dewpoint [%]")
ax[1].grid(True)

bars = ax[2].bar(x, bias, width=7, fc='r', ec='r')
for i, bar in enumerate(bars):
    if bias[i] < 0:
        bar.set_facecolor('b')
        bar.set_edgecolor('b')
ax[2].set_ylabel(r"Dewpoint bias $^\circ$F")
ax[2].grid(True)
ax[2].xaxis.set_major_formatter(mdates.DateFormatter('%-d %b'))

fig.savefig('test.png')