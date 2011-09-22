import iemdb
HADS = iemdb.connect('hads', bypass=True)
hcursor = HADS.cursor()

hcursor.execute("""
 select extract(epoch from valid), value from raw2011 where station = 'SSCN1' 
 and key = 'HGIRGZ' and valid > '2011-06-01' and value > 25 
 ORDER by valid ASC
""")
valid = []
rstage = []
for row in hcursor:
  valid.append( row[0] )
  rstage.append( row[1] )

import mx.DateTime
sts = mx.DateTime.DateTime(2011,6,1)
ets = mx.DateTime.DateTime(2011,9,1)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
xticks = []
xticklabels = []
while now < ets:
  if now.day in [1,15]:
    xticks.append( float(now) )
    xticklabels.append( now.strftime("%-d %b") )

  now += interval

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot( valid, rstage)
ax.plot( [min(valid), max(valid)], [27.0,27.0], color='black' )
ax.text( (max(valid) + min(valid)- (86400 * 14)) / 2.0, 27.1, 'Action Stage (27ft)', color='black')
ax.plot( [min(valid), max(valid)], [30.0,30.0], color='orange')
ax.text( (max(valid) + min(valid)- (86400 * 14)) / 2.0, 30.1, 'Flood Stage (30ft)', color='orange')
ax.plot( [min(valid), max(valid)], [33.0,33.0], color='red' )
ax.text( (max(valid) + min(valid)- (86400 * 14)) / 2.0, 33.1, 'Moderate Stage (33ft)', color='red')
ax.plot( [min(valid), max(valid)], [36.0,36.0], color='purple' )
ax.text( (max(valid) + min(valid) - (86400 * 14)) / 2.0, 36.1, 'Major Stage (36ft)', color='purple')
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels )
ax.set_xlim(min(valid) - 100000.0, max(valid) + 100000.0)
ax.set_ylim(26,38)
ax.grid(True)
ax.set_title("Missouri River at Sioux City (SSCN1) [1 Jun - 31 Aug 2011]")
ax.set_ylabel("Stage (ft)")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
