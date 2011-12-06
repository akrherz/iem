import numpy

import iemdb
import mx.DateTime
COOP = iemdb.connect('iem', bypass=True)
ccursor = COOP.cursor()

data = {'BRL': [], 'PAFA': [], 'MIA': []}

ccursor.execute("""
select day, max_tmpf, id from summary_2011 s JOIn stations t on (t.iemid = s.iemid) where t.id in ('BRL','MIA','PAFA') and day < '2011-11-22' ORDER by day ASC 
""")

for row in ccursor:
    data[row[2]].append( float(row[1]) )

xticks = []
xticklabels = []
for i in range(0,len(data['BRL'])):
  ts = mx.DateTime.DateTime(2011,1,1) + mx.DateTime.RelativeDateTime(days=i)
  if ts.day == 1:
    xticks.append( i )
    xticklabels.append( ts.strftime("%-d\n%b") )
  #elif (ts.day + 1) % 2 == 0:
  #  xticks.append( i )
  #  xticklabels.append( ts.strftime("%-d") )

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot( numpy.arange(len(data['BRL'])), data['BRL'], label="Burlington, IA")
ax.plot( numpy.arange(len(data['MIA'])), data['MIA'], label="Miami, FL")
ax.plot( numpy.arange(len(data['PAFA'])), data['PAFA'], label="Fairbanks, AK")
ax.grid(True)
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels)
#ax.set_xlim(0,len(highs)+2)
jul1 = int((mx.DateTime.DateTime(2011,7,1) - mx.DateTime.DateTime(2011,1,1)).days)
ax.set_xlim(jul1-1,335.5)
#ax.set_ylim(0,100)
ax.set_title("1 Jul - 21 Nov 2011 Daily High Temperatures")
ax.set_ylabel("High Temperature") 
ax.legend(loc=3)

jul7 = int((mx.DateTime.DateTime(2011,7,7) - mx.DateTime.DateTime(2011,1,1)).days)
ax.annotate("July 7: Three sites\nwithin 2$^{\circ}\mathrm{F}$", xy=(jul7, data['PAFA'][jul7] - 4),  xycoords='data',
                xytext=(10, -120), textcoords='offset points',
                bbox=dict(boxstyle="round", fc="0.8"),
                arrowprops=dict(arrowstyle="->",
                connectionstyle="angle3,angleA=0,angleB=-90"))

nov17 = int((mx.DateTime.DateTime(2011,11,17) - mx.DateTime.DateTime(2011,1,1)).days)
ax.annotate("Nov 17\nFairbanks: -31$^{\circ}\mathrm{F}$\nMiami: 85$^{\circ}\mathrm{F}$", xy=(nov17, data['PAFA'][nov17]),  xycoords='data',
                xytext=(-150, 0), textcoords='offset points',
                bbox=dict(boxstyle="round", fc="0.8"),
                arrowprops=dict(arrowstyle="->",
                connectionstyle="angle3,angleA=-90,angleB=0"))


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
