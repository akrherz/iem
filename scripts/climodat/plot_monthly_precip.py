"""
 Create a contour plot of monthly precip from the climodat data (iemre)
"""
import sys
import iemdb
import psycopg2.extras
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
import network
nt = network.Table("IACLIMATE")
import iemplot
import mx.DateTime

def do_month(ts, routes='m'):
    """
    Generate the plot for a given month, please
    """
    sql = """SELECT station, sum(precip) as total, max(day) as lastday
           from alldata_ia WHERE year = %s and month = %s
           and station != 'IA0000' and substr(station,2,1) != 'C'
           GROUP by station""" % (ts.year, ts.month)

    lats = []
    lons = []
    vals = []
    lastday = None
    ccursor.execute( sql )
    for row in ccursor:
        if not nt.sts.has_key(row['station']):
            continue
        if lastday is None:
            lastday = row['lastday']
        lats.append( nt.sts[row['station']]['lat'] )
        lons.append( nt.sts[row['station']]['lon'] )
        vals.append( row['total'] )
        
    cfg = {
     'wkColorMap': 'WhiteBlueGreenYellowRed',
     '_valid'    : '%s - %s' % (now.strftime("%d %B %Y"), lastday.strftime("%d %B %Y")),
     '_title'    : "%s Total Precipitation [inch]" % (now.strftime("%B %Y"),),
     'lbTitleString': 'inch',
     '_showvalues': True,
     '_format' : '%.2f',
     }

    tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
    pqstr = "plot %s %s summary/iemre_iowa_total_precip.png %s/summary/iemre_iowa_total_precip.png png" % (
                                    routes, ts.strftime("%Y%m%d%H%M"), 
                                                              ts.strftime("%Y/%m"),)
    iemplot.postprocess(tmpfp, pqstr)
    
if __name__ == '__main__':
    if len(sys.argv) == 3:
        now = mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]))
        do_month( now , 'm')
    else:
        now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1) + mx.DateTime.RelativeDateTime(day=1)
        do_month(now, 'cm')