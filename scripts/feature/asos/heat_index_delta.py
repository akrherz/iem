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
    otmpf.append(row[0])
    odwpf.append(row[1])

otmpf = dt.temperature(numpy.array(otmpf), 'F')
odwpf = dt.temperature(numpy.array(odwpf), 'F')
orelh = meteorology.relh(otmpf, odwpf)

tmpf = dt.temperature(numpy.arange(80, 110), 'F')
dwpf = dt.temperature(numpy.arange(40, 80), 'F')

(t, d) = numpy.meshgrid(tmpf.value("F"), dwpf.value("F"))

hindex = meteorology.heatindex(dt.temperature(t,'F'), dt.temperature(d, 'F'))
counts = numpy.zeros( numpy.shape(hindex.value("F")), 'f')
for otmp, odwp in zip(otmpf.value("F"), odwpf.value("F")):
    if odwp < 40 or odwp >= 79.5:
        continue
    counts[(int(round(odwp)) - 40), int(round(otmp)) - 80 ] += 1.0

ttot = numpy.sum(counts,0)
print ttot
ratio = numpy.ma.array(counts / ttot * 100.0)
#ratio.mask = numpy.where(ratio == 0, True, False)

(fig, ax) = plt.subplots(1,1)

cmap = cm.get_cmap('jet')
cmap.set_under("tan")
norm = mpcolors.BoundaryNorm([1,2,3,5,10,15,20,30,40,50,100], 256)

cs = ax.imshow( numpy.flipud(ratio), extent=(80,111, 40, 80), aspect='auto', 
           cmap=cmap, interpolation='nearest', norm=norm)

fig.colorbar(cs)

cs = ax.contour( hindex.value("F") - t, levels=[-5,-4,-3,-2,-1,0,2,4,6,8,10,14,20], 
                 extent=(80,110, 40, 80), aspect='auto', colors='white')
plt.clabel(cs, inline=1, fontsize=14, fmt='%.0f')

#print numpy.shape(otmpf)
#print numpy.shape(orelh)
#ax.scatter(otmpf.value("F"), orelh)

ax.set_xlim(80,110)
#ax.set_yticks([10,25,50,75,100])
ax.set_ylabel("Dew Point Temperature $^\circ$F")
ax.set_xlabel(r"Air Temperature $^\circ$F")
ax.set_title("1933-2012 Des Moines Heat Index\ncontour is heat index delta at temp/dwp\npixels are observed frequencies [%] at that temperature")
fig.tight_layout()
#fig.colorbar(cs)

fig.savefig('test.png')
