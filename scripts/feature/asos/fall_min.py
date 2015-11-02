# Generate current plot of air temperature

from pyiem.plot import MapPlot
import datetime
import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

vals = []
lats = []
lons = []
valmask = []
icursor.execute("""SELECT id, network, ST_x(geom) as lon,
    ST_y(geom) as lat, min(min_tmpf)
    from summary_2015 s JOIN stations t on (t.iemid = s.iemid)
    WHERE network IN ('IA_ASOS','AWOS') and min_tmpf > -50 and
    day > '2012-08-01' and id not in ('XXX')
    GROUP by id, network, lon, lat ORDER by min ASC""")
for row in icursor:
    vals.append(row[4])
    lats.append(row[3])
    lons.append(row[2])
    valmask.append(row[1] in ['IA_ASOS', 'AWOS'])
    print row[4], row[0]

m = MapPlot(title="2014-2015 Winter Minimum Temperature $^\circ$F",
            axisbg='white',
            subtitle=('Automated Weather Stations, Valid Fall 2014 - %s'
                      ) % (datetime.datetime.now().strftime("%d %b %Y"),))
# m.contourf(lons, lats, vals, np.arange(-30,1,4))
m.plot_values(lons, lats, vals, '%.0f', valmask)
m.drawcounties()
m.postprocess(filename='150223.png')
