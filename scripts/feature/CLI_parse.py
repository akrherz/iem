import iemdb
import network
nt = network.Table(('IA_ASOS','MO_ASOS','IL_ASOS', 'ND_ASOS', 'AWOS',
          'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS',
          'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS', 'WFO'))
AFOS = iemdb.connect('afos', bypass=True)
acursor = AFOS.cursor()
acursor2 = AFOS.cursor()



acursor.execute("""SELECT distinct pil from products_2014_0106 where
 substr(pil,1,3) = 'CLI' and entered > '2014-06-23' """)

lats = []
lons = []
vals = []

for row in acursor:
    stid = row[0][-3:]
    if stid in ['RAP', 'DVN', 'FGF', 'OAX', 'MPX']:
        continue
    if not nt.sts.has_key(row[0][-3:]):
        continue
    if nt.sts[stid]['state'] in ['WY', 'CO']:
        continue
    acursor2.execute("""
    SELECT data from products_2014_0106 WHERE pil = %s 
    and entered > '2014-06-23' ORDER by entered DESC
    LIMIT 1
    """, (row[0],))
    row2 = acursor2.fetchone()
    hasSnowfall = False
    for line in row2[0].split("\n"):
        if line.find("PRECIPITATION (IN)") > -1:
            hasSnowfall = True
        if line.strip() == "":
            hasSnowfall = False
        if hasSnowfall and line.find("SINCE JUN 1") > 0:
            tokens = line.split()
            if len(tokens) < 6:
                break
            if tokens[5] not in ['MM','T'] and float(tokens[5]) > -77:
                print row[0], tokens[5], tokens
                lats.append( nt.sts[row[0][-3:]]['lat'])
                lons.append( nt.sts[row[0][-3:]]['lon'])
                vals.append( float(tokens[5]) )
            break
        
from pyiem.plot import MapPlot

m = MapPlot(sector='midwest',
       title='NWS June Precipitation Departure (inches) thru 22 June 2014',
       subtitle= '1-22 June 2014 based on NWS issued CLI Reports')
m.plot_values(lons, lats, vals, fmt='%.1f')
m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')
