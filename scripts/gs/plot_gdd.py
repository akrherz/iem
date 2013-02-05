"""
 Generate a plot of GDD 
"""

import sys
import os
import iemplot
import datetime

import psycopg2
COOP = psycopg2.connect("dbname=coop host=iemdb user=nobody")
ccursor = COOP.cursor()

import network
nt = network.Table("IACLIMATE")

def run(base, ceil, now, fn):
    """ Generate the plot """
    # Compute normal from the climate database
    sql = """SELECT station,
       sum(gddxx(%s, %s, high, low)) as gdd
       from alldata_ia WHERE year = %s and month in (5,6,7,8,9,10)
       and station != 'IA0000' and substr(station,2,1) != 'C'
       GROUP by station""" % (base, ceil, now.year)

    lats = []
    lons = []
    gdd50 = []
    ccursor.execute( sql )
    for row in ccursor:
        if not nt.sts.has_key(row[0]):
            continue
        lats.append( nt.sts[row[0]]['lat'] )
        lons.append( nt.sts[row[0]]['lon'] )
        gdd50.append( row[1] )

    cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_title'             : "Iowa 1 May - %s GDD Accumulation" % (
                        now.strftime("%-d %B %Y"), ),
 'lbTitleString'      : "base %s" % (base,),
}
    # Generates tmp.ps
    tmpfp = iemplot.simple_contour(lons, lats, gdd50, cfg)

    pqstr = "plot c 000000000000 summary/%s.png bogus png" % (fn,)
    iemplot.postprocess(tmpfp, pqstr)

if __name__ == '__main__':
    today = datetime.datetime.now()
    if today.month < 5:
        today = today.replace(year=(today.year-1), month=11, day=1)
    run(50,86, today, 'gdd_may1')
    run(60,86, today, 'gdd_may1_6086')
    run(65,86, today, 'gdd_may1_6586')