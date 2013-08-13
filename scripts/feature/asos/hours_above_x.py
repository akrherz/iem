import iemdb
import numpy as np

ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

data = np.zeros( (2014-1935, 90-50), 'f') # 50 to 90
cnts = np.zeros( (2014-1935) )

acursor.execute("""
    SELECT to_char(valid, 'YYYYMMDDHH24') as d, max(dwpf) from alldata 
    where station = 'DSM' and extract(doy from valid) between 151 and 224 
    and valid > '1935-01-01' and dwpf > 0 group by d""")
for row in acursor:
    year = int(row[0][:4])
    cnt = 1
    if year >= 1965 and year < 1973:
        cnt = 3
    dwpf = int(round(row[1]))
    if dwpf >= 50:
        data[year-1935,:dwpf-50] += cnt
    cnts[year-1935] += cnt

import matplotlib.pyplot as plt

avgs = np.average(data,0)

idx = np.argmax( data[:,26])
idx2 = np.argmin( data[:,16])
totalhrs =  (225 - 151) * 24.0

(fig, ax) = plt.subplots(2,1)

ax[0].plot(np.arange(50,90), avgs / totalhrs * 100., label='Average', lw=2., c='k')
ax[0].plot(np.arange(50,90), data[-1,:]/ totalhrs * 100., label='2013', lw=2, c='g')
ax[0].plot(np.arange(50,90), data[idx,:]/ totalhrs * 100., label='%s' % (idx+1935,), lw=2, c='b')
ax[0].plot(np.arange(50,90), data[idx2,:]/ totalhrs * 100., label='%s' % (idx2+1935,), lw=2, c='r')
ax[0].legend()
ax[0].set_yticks([0,10,25,50,75,90,100])
ax[0].set_title("1935-2013 (1 Jun - 12 Aug) Des Moines Hourly Dew Point")
ax[0].grid(True)
ax[1].grid(True)
ax[0].set_xlabel(r"Dew Point Temperature $^\circ$F")
ax[0].set_ylabel("Percentage of Hours AOA")

ax[1].bar(np.arange(1935,2014)-0.4, data[:,0] / totalhrs * 100., ec='b', fc='b')
ax[1].set_xlim(1934.5, 2013.5)
ax[1].set_ylabel("Percent Hours AOA 50$^\circ$F")
ax[1].set_ylim(70,100)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')