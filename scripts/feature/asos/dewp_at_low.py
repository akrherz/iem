import psycopg2
import numpy as np
import datetime
import network

nt = network.Table("IA_ASOS")

ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()

x = []
for i in range(53):
    ts = datetime.datetime(2000,1,1) + datetime.timedelta(days=i*7)
    x.append( ts.strftime("%b") if ts.day < 8 else "")


def do(stid):

    acursor.execute("""
   select date, avg(vsby) from 
     (select date(valid), tmpf, dwpf, sknt, vsby,
      rank() over (PARTITION by date(valid) ORDER by tmpf ASC) from alldata
      where station = %s and valid > '1996-01-01'
      and extract(month from valid) in (6,7,8)) as foo 
   WHERE rank = 1 and tmpf - dwpf < 90 and vsby >= 0 and vsby <= 10 GROUP by date
    """, (stid,))
    vals = []
    for row in acursor:
        vals.append( row[1] )
    
    return vals
 
data = []
labels = []
keys = nt.sts.keys()
keys.sort()
for sid in keys:
    print sid
    data.append( do(sid) )
    labels.append( nt.sts[sid]['name'].replace(" ", "\n").title() )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.set_title("Visibility at time of Daily Low Temperature\n1996-2013 over months of June, July, August")
#ax.set_ylabel("Dewpoint Depression $^\circ$F")
ax.set_ylabel("Visibility [miles]")
ax.boxplot(data)
ax.set_xticklabels(labels, rotation=-90)
ax.set_ylim(0,12)
#ax.set_yticks([0,1,2,3,4,5,7,10,15,20,25])
#ax.set_yticklabels(['',1,'',3,'',5,10,15,20,25])
ax.grid(True, axis='y')
fig.tight_layout()

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')