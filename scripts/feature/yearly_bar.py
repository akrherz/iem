import iemdb, network
import numpy
import mx.DateTime

POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

count = numpy.zeros((26,), 'f')
area = numpy.zeros((26,), 'f')

def fetcher():
    for yr in range(1986,2012):
        # Cnts
        pcursor.execute("""
        select distinct wfo, eventid, phenomena from warnings_%s 
        where significance = 'W' and phenomena in ('SV','TO')
        """ % (yr,))
        count[yr-1986] = pcursor.rowcount 
    
        # Area
        gtype = 'C'
        if yr > 2007:
            gtype = 'P'
        pcursor.execute("""
        select sum(ST_Area(ST_Transform(geom,2163)) / 1000000.0) / 7663941.7 from 
        warnings_%s where significance = 'W' and phenomena in ('SV','TO')
        and gtype = '%s'
        """ % (yr, gtype))
        row = pcursor.fetchone()
        area[yr-1986] =  row[0] 

    print tuple(count)
    print tuple(area)
#fetcher()
count = numpy.array(
              [7295.0, 6328.0, 5967.0, 8280.0, 9469.0, 10364.0, 11202.0, 
               11967.0, 14331.0, 19230.0, 21055.0, 19663.0, 26248.0, 
               20303.0, 20949.0, 20311.0, 19820.0, 23307.0, 23601.0, 
               23783.0, 26944.0, 23801.0, 31262.0, 24099.0, 22762.0, 
               30123.0      ]
                    )
area = numpy.array(
            [3.411617, 3.0034876, 2.7862113, 3.565259, 4.2773128, 
             4.7449946, 4.9574609, 5.1155105, 6.003407, 8.2048721, 
             10.543365, 10.398357, 11.114855, 9.9166527, 9.3769169, 
             10.052322, 9.5221882, 10.569538, 11.562414, 13.049739, 
             13.48593, 13.411092, 6.5910234, 5.187911, 5.225493, 7.2291718]
                   )

import matplotlib.pyplot as plt
import iemplot

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar( numpy.arange(1986, 2012) - 0.3, count, width=0.3,
        facecolor='#FF0000', edgecolor='#FF0000', zorder=1, label='Count')
ax.set_xlim(1985.5, 2011.5)
ax.set_ylabel("Number of Warnings", color='red')
ax.set_title("NWS Severe T'Storm + Tornado Warnings [1986-2011]")
ax.set_xlabel(" * 2008-2011 Are Storm Based Warnings ")
ax.grid(True)

ax2 = ax.twinx()
bars2 = ax2.bar( numpy.arange(1986, 2012), area, label='Area',
        facecolor='#0000FF', edgecolor='#0000FF', width=0.3, zorder=1)
ax2.set_xlim(1985.5, 2011.5)
ax2.set_ylabel("Total Area [x CONUS]", color='blue')

ax2.legend( [bars[0], bars2[0]], ['Count', 'Area'], loc=2)

fig.savefig('test.ps')
iemplot.makefeature('test')
