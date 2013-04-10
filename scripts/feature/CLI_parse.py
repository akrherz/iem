import iemdb
import network
nt = network.Table(('IA_ASOS','MO_ASOS','IL_ASOS', 'ND_ASOS', 'AWOS',
          'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS',
          'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS', 'WFO'))
AFOS = iemdb.connect('afos', bypass=True)
acursor = AFOS.cursor()
acursor2 = AFOS.cursor()



acursor.execute("""SELECT distinct pil from products_2013_0106 where
 substr(pil,1,3) = 'CLI' and entered > '2013-03-01' """)

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
    SELECT data from products_2013_0106 WHERE pil = %s 
    and entered > '2013-03-01' ORDER by entered DESC
    LIMIT 1
    """, (row[0],))
    row2 = acursor2.fetchone()
    hasSnowfall = False
    for line in row2[0].split("\n"):
        if line.find("SNOWFALL (IN)") > -1:
            hasSnowfall = True
        if line.strip() == "":
            hasSnowfall = False
        if hasSnowfall and line.find("SINCE JUL 1") > 0:
            tokens = line.split()
            if tokens[3] not in ['MM','T'] and float(tokens[3]) > 0:
                print row[0], tokens
                lats.append( nt.sts[row[0][-3:]]['lat'])
                lons.append( nt.sts[row[0][-3:]]['lon'])
                vals.append( float(tokens[3]) )
            break
        
import iemplot

cfg = {'_midwest': True,
       '_showvalues': True,
       '_title': 'NWS Total Snowfall (inches) thru 7 March 2013',
       '_valid': '1 July 2012 - 7 March 2013',
       '_format': '%.0f'}
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)