"""
http://www.srh.noaa.gov/images/ffc/pdf/ta_htindx.PDF
"""
import numpy
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mpcolors
import psycopg2
from pyiem.datatypes import temperature
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
    
otmpf = temperature(numpy.array(otmpf), 'F')
odwpf = temperature(numpy.array(odwpf), 'F')
orelh = meteorology.relh(otmpf, odwpf)


def calc(tmpf, relh):
    """ There is no straightfoward equation, we have approximations to 
    tables 
    
    Stull, Richard (2000). Meteorology for Scientists and Engineers, 
    Second Edition. Brooks/Cole. p. 60. ISBN 9780534372149.
    
    """
    return (16.923 + 0.185212 * tmpf 
            + 5.37941 * relh
            - 0.100254 * tmpf * relh 
            + 0.00941695 * tmpf ** 2
            + 0.00728898 * relh ** 2 
            + 0.000345372 * tmpf ** 2 * relh
            - 0.000814971 * tmpf * relh**2 
            + 0.0000102102 * tmpf **2 * relh **2
            - 0.000038646 * tmpf ** 3 
            + 0.0000291583 ** relh ** 3
            + 0.00000142721 * tmpf ** 3 * relh
            + 0.000000197483 * tmpf * relh ** 3
            - 0.00000002184429 * tmpf ** 3 * relh ** 2
            + 0.000000000943296 * tmpf ** 2 * relh ** 3
            - 0.0000000000418975 * tmpf ** 3 * relh ** 3)

    # Below is more exact for a small range of values, 
    # The Assessment of Sultriness. Part II: Effects of Wind, Extra Radiation 
    # and Barometric Pressure on Apparent Temperature Journal of Applied 
    # Meteorology, R. G. Steadman, July 1979, Vol 18 No7, pp874-885
#    return (-42.379 + 2.04901523 * tmpf + 10.14333127 * relh 
#         - 0.22475541 * tmpf * relh - 0.00683783 * tmpf ** 2
#         - 0.05481717 * relh ** 2 + 0.00122874 * tmpf ** 2 * relh
#         + 0.00085282 * tmpf * relh ** 2 - 0.00000199 * tmpf ** 2 * relh ** 2
#         )
    
tmpf = numpy.arange(80,110)
relh = numpy.arange(10,101,2)

(t, r) = numpy.meshgrid(tmpf, relh)

hindex = calc(t, r)
counts = numpy.zeros( numpy.shape(hindex), 'f')
for otmp, orel in zip(otmpf.value("F"), orelh):
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

cs = ax.contour( hindex - t, levels=[-5,-4,-3,-2,-1,0,2,4,6,8,10,14,20], 
                 extent=(80,110, 10, 101), aspect='auto', colors='white')
plt.clabel(cs, inline=1, fontsize=14, fmt='%.0f')

print numpy.shape(otmpf)
print numpy.shape(orelh)
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
