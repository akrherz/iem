import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

x = []
y = []
data = []
for yr in range(1986,2011):
    pcursor.execute("""
    select avg( x(ST_Centroid(geom)) ) , avg( y(ST_Centroid(geom)) ) 
    from warnings_%s where issue BETWEEN '%s-03-01' and '%s-04-01' 
    and phenomena in ('SV','TO') and gtype = 'C' and 
    significance = 'W'
    """ % (yr, yr, yr))
    row = pcursor.fetchone()
    x.append( float(row[0]) )
    y.append( float(row[1]) )
    
    ccursor.execute("""
    SELECT avg((high+low)/2.0) from alldata WHERE
    stationid = 'ia0000' and year = %s and month = 3
    """ % (yr,))
    row = ccursor.fetchone()
    data.append( float(row[0]) )

cfg = {
       '_title': "Iowa Avg March Temp [F] plotted at center of SVR,TOR Warnings",
       '_valid': '1986-2010',
       '_showvalues': True,
       '_format': '%.0f',
       '_spatialDataLimiter': [min(x), min(y), max(x), max(y)],
       'mpOutlineSpecifiers':  ["Conterminous US : Arkansas",
                                "Conterminous US : Mississippi",
                                "Conterminous US : Oklahoma",
                                "Conterminous US : Texas",
                                "Conterminous US : Kentucky",
                                "Conterminous US : Tennessee",
                                "Conterminous US : Missouri",
                                "Conterminous US : Lousiana"]
       }
import iemplot
tmpfp = iemplot.simple_valplot(x,y,data,cfg)
#iemplot.postprocess(tmpfp, '', '')
iemplot.makefeature(tmpfp)
""" 
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

print x
print y
ax.scatter(x, y)

fig.savefig('test.png')
""" 