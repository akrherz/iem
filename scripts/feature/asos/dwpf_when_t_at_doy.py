import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute("""
 SELECT valid, extract(doy from valid), tmpf, round(dwpf::numeric,0) from alldata WHERE
 station = 'DSM' and tmpf >= 90 and dwpf > 0
""")
total_dwpf = [0]*366
cnt_doy = [0]*366
import numpy.ma
data = numpy.ma.zeros( (100,366), 'f')

for row in acursor:
    data[int(row[3])-2:int(row[3])+2,int(row[1])-2:int(row[1])+2] += 1
    #doy.append( float(row[1]) )
    #dwpf.append( float(row[3]) )
    total_dwpf[int(row[1])-1] += float(row[3])
    cnt_doy[int(row[1])-1] += 1

gdoy = []
gdwpf = []
for i in range(0,366):
    if cnt_doy[i] > 10:
        gdoy.append( i-1 )
        gdwpf.append( total_dwpf[i]/float(cnt_doy[i]))

import matplotlib.pyplot as plt
fig, ax = plt.subplots(1,1, figsize=(8,6))

data.mask = numpy.where( data == 0, True, False)
res = ax.imshow( data / numpy.ma.max(data), aspect='auto', rasterized=True, interpolation='nearest')
ax.set_ylim(20,90)
fig.colorbar( res )
#ax.scatter(doy, dwpf, color='red', edgecolor='red')
#ax.plot(gdoy, gdwpf, color='k', lw=2, label="Average")
ax.grid(True)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_title("Des Moines Dew Point when Air Temperature >= 90$^{\circ}\mathrm{F}$\nRelative Frequency Plotted")
ax.set_ylabel("Dew Point $^{\circ}\mathrm{F}$")
ax.set_xlabel("Day of Year [1933-2012]")
#ax.legend()
ax.set_xlim(100,300)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')