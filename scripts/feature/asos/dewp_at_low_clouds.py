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
   select date, max(clouds), avg(tmpf), avg(dwpf) from 
     (select date(valid), (case when 
     (skyc1 in ('OVC','BKN') and skyl1 < 12000) or
     (skyc2 in ('OVC','BKN') and skyl2 < 12000)  or 
     (skyc3 in ('OVC','BKN') and skyl3 < 12000)  or 
     (skyc4 in ('OVC','BKN') and skyl4 < 12000) 
     then 1 else 0 end) as clouds, tmpf, dwpf, 
      rank() over (PARTITION by date(valid) ORDER by tmpf ASC) from alldata
      where station = %s and valid > '1996-01-01'
      and extract(month from valid) in (6,7,8)) as foo 
   WHERE rank = 1  GROUP by date
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
    vals = do(sid)
    data.append( sum(vals) / float(len(vals)) * 100.0 )
    labels.append( nt.sts[sid]['name'].replace(" ", "\n").title() )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.set_title("Overcast/Broken Sky Coverage <12kft at time of Daily Low Temp\n1996-2013 over months of June, July, August")
#ax.set_ylabel("Dewpoint Depression $^\circ$F")
ax.set_ylabel("Percentage [%]")
#ax.boxplot(data)
ax.bar(np.arange(len(labels))-0.4, data)
ax.set_xticklabels(labels, rotation=-90)
ax.set_ylim(0,100)
ax.set_xlim(-0.5, 14.5)
ax.set_xticks( range(len(labels)))
#ax.set_yticks([0,1,2,3,4,5,7,10,15,20,25])
#ax.set_yticklabels(['',1,'',3,'',5,10,15,20,25])
ax.grid(True, axis='y')
fig.tight_layout()

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')