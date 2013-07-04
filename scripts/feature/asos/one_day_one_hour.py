import numpy as np
import psycopg2

conn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = conn.cursor()

cursor.execute("""
  SELECT valid, dwpf, p01i,
  case when skyc1 in ('BKN','OVC') or skyc2 in ('BKN','OVC') or 
        skyc3 in ('BKN','OVC') then 1 else 0 end  as clouds, presentwx,
        tmpf
 from alldata where station = 'DSM' and
  extract(hour from valid + '10 minutes'::interval) = 22 and
  extract(minute from valid) in (54,0) and
  extract(day from valid) = 4 and extract(month from valid) = 7
  and valid > '1951-01-01' 
  ORDER by valid ASC
""")

data = np.zeros( (4, 2013-1951), 'f')
for row in cursor:
    offset = row[0].year - 1951
    if row[1] >= 65:
        data[0,offset] = 1.
    if row[2] > 0 or (row[4] is not None and row[4].find('RA') > -1):
        data[2,offset] = 1.
    if row[3] > 0:
        data[3,offset] = 1.
    if row[5] >= 80:
        data[1,offset] = 1.
        
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)
ax.set_title("1951-2012 Des Moines 10 PM Weather on July 4$^\mathrm{th}$\nnumbers at top are number out of four conditions meet")
#ax.imshow( data, extent=(1951,2013,3,0), aspect='auto', 
#           interpolation='nearest')
shp = np.shape( data )
for i in range(shp[1]):
    for j in range(shp[0]):
        if data[j,i] > 0:
            ax.scatter(i+1951, j, marker='*', s=50)
ss = np.sum(data,0)
ss2 = np.sum(data,1)
for i,s in enumerate(ss):
    
    ax.text(i+1951, 3.3 + float(s) / 10., "%.0f" % (s,), ha='center', va='center')
ax.set_xlim(1950,2013)
ax.set_yticks((0,1,2,3))
ax.set_ylim(-0.3, 3.7)
ax.set_yticklabels(("Dew Point\nOver 65$^\circ$F\n%.0f/62\n%.1f%%" % (ss2[0], ss2[0]/62.0*100.0), 
                    "Temp\nOver 80$^\circ$F\n%.0f/62\n%.1f%%" % (ss2[1], ss2[1]/62.0*100.0), 
                    "Raining\n%.0f/62\n%.1f%%" % (ss2[2], ss2[2]/62.0*100.0), 
                    "Cloudy\n%.0f/62\n%.1f%%" % (ss2[3], ss2[3]/62.0*100.0)))
ax.grid(True)

fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')