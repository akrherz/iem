import iemdb, network
import numpy
import iemplot
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

lats = []
lons = []
delta = []
nt = network.Table('IACLIMATE')
for id in nt.sts.keys():
    if id in ['IA0000', 'IA1635']:
        continue
    # Get yearly precip since 1951
    data = numpy.zeros( (60,), numpy.float)
    ccursor.execute("""
    SELECT year, avg((high+low)/2.0) from alldata where stationid = %s and year < 2011
    and year > 1950  GROUP by year ORDER by year ASC
    """, (id.lower(),))
    for row in ccursor:
        data[ row[0] - 1951 ] = row[1]
        
    d2011 = numpy.average( data[56:60] )
    d1981 = numpy.average( data[26:56] )
    print id, d2011, d1981
    delta.append( d2011 - d1981 )
    lats.append( nt.sts[id]['lat'] )
    lons.append( nt.sts[id]['lon'] )
    

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd': 2,
 '_title'             : "Past Four Year Precipitation Departure (inch per year)",
 '_valid'             : "[2007-2010] minus [1977-2006]",
 '_showvalues'        : True,
 '_format'            : '%.1f',
 'lbTitleString'      : "[inch]",
 'cnLevelSelectionMode': 'ManualLevels',
 'cnLevelSpacingF'      : 2.0,
 'cnMinLevelValF'       : -16.0,
 'cnMaxLevelValF'       : 16.0,

       }

fp = iemplot.simple_contour(lons, lats, delta, cfg)
iemplot.postprocess(fp, '', '')
#iemplot.makefeature(fp)
