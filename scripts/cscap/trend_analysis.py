import iemplot
import network
import iemdb
import numpy
#from scipy import stats
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

nt = network.Table(("IACLIMATE", "MNCLIMATE", "NDCLIMATE", "SDCLIMATE",
 "NECLIMATE", "KSCLIMATE", "MOCLIMATE", "KYCLIMATE", "ILCLIMATE", "WICLIMATE",
 "INCLIMATE", "OHCLIMATE", "MICLIMATE"))

vals = []
lats = []
lons = []

def dbload():
    output = open('cache.csv', 'w')
    for id in nt.sts.keys():
        #if id[2] == 'C' or id[2:] == '0000':
        #    continue
        ccursor.execute("""
         SELECT year, sum(precip) from alldata_%s 
         where year > 1950 
         and station = '%s' and year < 2011
         GROUP by year ORDER by year ASC
        """ % (id[:2], id))
        yearly = []
        years = []
        for row in ccursor:
            years.append( row[0] )
            yearly.append( row[1] )
        h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(years, yearly)
        print '%7.4f %s' % (h_slope, id)
        vals.append( h_slope )
        lats.append( nt.sts[id]['lat'] )
        lons.append( nt.sts[id]['lon'] )
        output.write('%.4f,%.4f,%.4f,%.4f,%s,%s\n' % (nt.sts[id]['lon'],
                    nt.sts[id]['lat'], h_slope, h_r_value,
                    id, nt.sts[id]['name']))
    output.close()
    
def cached():
    for line in open('cache.csv'):
        tokens = line.split(",")
        if float(tokens[3]) < 0.33:
            continue
        vals.append( float(tokens[2]) )
        lats.append( float(tokens[1]) )
        lons.append( float(tokens[0]) )
 
#dbload()
cached()
cfg = {'_title': "Annual Precipitation Departure",
       'lbTitleString': 'inch',
       '_midwest': True}
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.postprocess(tmpfp, None, fname='test.png')
