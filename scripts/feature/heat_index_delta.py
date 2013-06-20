"""
http://www.srh.noaa.gov/images/ffc/pdf/ta_htindx.PDF
"""
import numpy
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mpcolors
import psycopg2
import pyiem.datatypes as dt
from pyiem import meteorology

dbconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = dbconn.cursor()

otmpf = []
odwpf = []
cursor.execute("""SELECT tmpf, dwpf from alldata where station = 'DSM' and
 tmpf >= 80 and dwpf > 0 and tmpf < 110""")
for row in cursor:
    otmpf.append( row[0] )
    odwpf.append( row[1] )
    
otmpf = dt.temperature(numpy.array(otmpf), 'F')
odwpf = dt.temperature(numpy.array(odwpf), 'F')
orelh = meteorology.relh(otmpf, odwpf)

tmpf = dt.temperature(numpy.arange(80,110), 'F')
relh = dt.humidity(numpy.arange(10,101,2), '%')

(t, r) = numpy.meshgrid(tmpf.value("F"), relh.value("%"))

hindex = meteorology.heatindex(dt.temperature(t,'F'), dt.humidity(r, '%'))
counts = numpy.zeros( numpy.shape(hindex.value("F")), 'f')
for otmp, orel in zip(otmpf.value("F"), orelh.value("%")):
    counts[(int(round(orel)) - 10) /2, int(round(otmp)) - 80 ] += 1.0

ttot = numpy.sum(counts,0)
print ttot
ratio = numpy.ma.array(counts / ttot * 100.0)
#ratio.mask = numpy.where(ratio == 0, True, False)

(fig, ax) = plt.subplots(1,1)

cmap = cm.get_cmap('jet')
cmap.set_under("tan")
norm = mpcolors.BoundaryNorm([1,10,20,30,40,50,60,70,80,90,100], 256)

cs = ax.imshow( numpy.flipud(ratio), extent=(80,111, 10, 101), aspect='auto', 
           cmap=cmap, interpolation='nearest', norm=norm)

fig.colorbar(cs)

cs = ax.contour( hindex.value("F") - t, levels=[-5,-4,-3,-2,-1,0,2,4,6,8,10,14,20], 
                 extent=(80,110, 10, 101), aspect='auto', colors='white')
plt.clabel(cs, inline=1, fontsize=14, fmt='%.0f')

#print numpy.shape(otmpf)
#print numpy.shape(orelh)
#ax.scatter(otmpf.value("F"), orelh)

ax.set_xlim(80,110)
ax.set_yticks([10,25,50,75,100])
ax.set_ylabel("Relative Humidity [%]")
ax.set_xlabel(r"Air Temperature $^\circ$F")
ax.set_title("1933-2012 Des Moines Heat Index\ncontour is heat index delta at temp/relh\npixels are observed frequencies [%] at that temperature")
fig.tight_layout()
#fig.colorbar(cs)

fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')
