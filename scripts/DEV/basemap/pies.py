from pyiem.plot import MapPlot
from matplotlib.collections import PatchCollection
from matplotlib.patches import Wedge
import matplotlib.patheffects as PathEffects

from pyiem import network
nt = network.Table("IA_ASOS")
import psycopg2
PGCONN = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = PGCONN.cursor()

data = [
        ['IOW', 4.12, 10.89, 'Iowa City'],
        ['OTM', 6.34, 12.36, 'Ottumwa'],
        ['SUX', 13.25, 8.78, 'Sioux City'],
        ['MCW', 6.75, 13.45, 'Mason City'],
        ['DBQ', 9.81, 14.28, 'Dubuque'],
        ['ALO', 6.37, 12.47, 'Waterloo'],
        ['DSM', 3.61, 15.79, 'Des Moines'],
        ['BRL', 8.52, 11.34, 'Burlington'],
        ['CID', 8.93, 12.02, 'Cedar Rapids'],
        ['EST', 9.09, 13.49, 'Esterville'],
        ['MIW', 5.27, 14.61, 'Marshalltown']
]
patches = []
m = MapPlot(sector='iowa',
            title='Amount of additional June precipitation needed to break local record',
            subtitle='1-23 June 2014 totals shown')

for row in data:
    #cursor.execute("""SELECT year, sum(precip) from alldata_ia where month =6
    #and year < 2014 and station = %s 
    #GROUP by year ORDER by sum DESC LIMIT 1""", (nt.sts[row[0]]['climate_site'],) )
    #row2 = cursor.fetchone()

    #ratio = row[1] / row2[1] * 360.
    #print row[0], row[1], row2[1], ratio
    ratio = min(row[1] / row[2] * 360., 360.)
    

    xy = m.map(nt.sts[row[0]]['lon'], nt.sts[row[0]]['lat'])
    patches.append(
        Wedge(xy, 20000, 0, ratio, width=10000, fc='b', fill=True, zorder=2)
                   )
    print "%.0f" % (ratio/360. * 100.,), ratio / 360.0
    remaining = max(0, row[2] - row[1])
    txt = m.ax.text(xy[0], xy[1], "%.2f" % (remaining,), fontsize=24, color='yellow',
              ha='center', va='center')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                        foreground="purple")])

    txt = m.ax.text(xy[0], xy[1]-12000, "%s" % (row[3],), fontsize=14,
              ha='center', va='center')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                        foreground="yellow")])


p = PatchCollection(patches)
m.ax.add_collection(p)

m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')