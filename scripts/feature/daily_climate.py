import iemdb, numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("SELECT valid, max_high from climate where station = 'IA5230' and extract(month from valid) = 3 ORDER by valid ASC")

records = [0]*31

for row in ccursor:
  records[ row[0].day - 1] = row[1]

records[10] = 64
records = numpy.array(records)

ccursor.execute("""SELECT day, high from alldata_ia where station = 'IA5230' and day > '2012-02-29' ORDER by day ASC""")
obs = [0]*20
for row in ccursor:
  obs[ row[0].day - 1] = row[1]

obs[14] = 74
obs[15] = 79
obs[16] = 77
obs[17] = 75
obs[18] = 72
obs[19] = 68

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar( numpy.arange(1,21)-0.4, obs, width=0.8 , fc='skyblue', label='2012')
ax.bar( numpy.arange(1,32)-0.5, [0.25]*31, bottom=records-0.25, width=1, fc='k', ec='k', label="Record")
for i in range(-5,0):
  bars[i].set_facecolor("teal")

ax.set_xlim(9.5,20.5)
ax.set_ylim(50,85)
ax.grid(True)
ax.set_title("10-20 March 2012 : Mason City High Temperatures")
ax.set_xlabel("16-20 Forecasted")
ax.set_ylabel("High Temperature $^{\circ}\mathrm{F}$")
ax.legend(loc=2)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
