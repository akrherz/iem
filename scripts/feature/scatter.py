
import iemdb
from matplotlib import pyplot as plt
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()

#  min(case when extract(month from day) in (8,9) then low else 100 end), 
ccursor.execute("""SELECT sum(case when extract(month from day) in (8)
  then precip else 0 end),
  min( case when low < 32 then extract(doy from day) else 366 end),
  year from alldata where stationid = 'ia0200' and 
  sday >= '0601'  GROUP by year""")
precip = []
lows = []
for row in ccursor:
  precip.append( row[0] )
  lows.append( row[1] )

print precip
fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(precip, lows, color='black', marker="+")
ax.set_title("Hello")

plt.savefig("test.png")
