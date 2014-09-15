import psycopg2
RWIS = psycopg2.connect(database='rwis', host='iemdb', user='nobody')
cursor = RWIS.cursor()

cursor.execute("""
  SELECT valid, tfs1, tmpf, dwpf, tfs1_text from t2013 where station = 'RAMI4' 
  and valid > '2013-11-16' and valid < '2013-11-17' ORDER by valid ASC
  """)
valid = []
obs = []
tmpf = []
dwpf = []
for row in cursor:
    valid.append( row[0] )
    obs.append( row[1] )
    tmpf.append( row[2] )
    dwpf.append( row[3] )

import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
(fig, ax) = plt.subplots(2,1)

ax[0].plot(valid, obs, label='Pavement', lw=2, c='brown')
ax[0].plot(valid, tmpf, label='Air', linestyle='-.', lw=2, c='r')
ax[0].plot(valid, dwpf, label='Dew Point', linestyle='-.', lw=2, c='b')
ax[0].grid(True)
ax[0].legend(loc=2, fontsize=12)
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%-I %p',
                                tz=pytz.timezone('America/Chicago')))

ax[0].set_title("16 Nov 2013: Ames RWIS Timeseries of Temperatures")
ax[0].set_ylabel('Temperature $^{\circ}\mathrm{F}$')

fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
