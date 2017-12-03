#!/usr/bin/env python
"""
 Produce a OA GDD Plot, dynamically!
"""
import sys
import os
import cgi
import datetime

from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    COOP = get_dbconn('coop', user='nobody')
    ccursor = COOP.cursor()
    
    form = cgi.FieldStorage()
    if ("year1" in form and "year2" in form and 
        "month1" in form and "month2" in form and
        "day1" in form and "day2" in form):
        sts = datetime.datetime(int(form["year1"].value), 
          int(form["month1"].value), int(form["day1"].value))
        ets = datetime.datetime(int(form["year2"].value), 
          int(form["month2"].value), int(form["day2"].value))
    else:
        sts = datetime.datetime(2011,5,1)
        ets = datetime.datetime(2011,10,1)
    baseV = 50
    if "base" in form:
        baseV = int(form["base"].value)
    maxV = 86
    if "max" in form:
        maxV = int(form["max"].value)
    
    
    # Make sure we aren't in the future
    now = datetime.datetime.today() 
    if ets > now:
        ets = now
    
    st = NetworkTable("IACLIMATE")
    # Now we load climatology
    #sts = {}
    #rs = mesosite.query("SELECT id, x(geom) as lon, y(geom) as lat from stations WHERE \
    #    network = 'IACLIMATE'").dictresult()
    #for i in range(len(rs)):
    #    sts[ rs[i]["id"].lower() ] = rs[i]
    
    
    # Compute normal from the climate database
    sql = """SELECT station,
       sum(gddXX(%s, %s, high, low)) as gdd, count(*)
       from alldata_ia WHERE year = %s and day >= '%s' and day < '%s'
       and substr(station, 2, 1) != 'C' and station != 'IA0000'
       GROUP by station""" % (baseV, maxV, sts.year, sts.strftime("%Y-%m-%d"),
                                ets.strftime("%Y-%m-%d"))
    
    lats = []
    lons = []
    gdd50 = []
    valmask = []
    ccursor.execute(sql)
    total_days = (ets - sts).days
    for row in ccursor:
      id = row[0]
      if not st.sts.has_key(id):
        continue
      if row[2] < (total_days * 0.9):
        continue
      lats.append( st.sts[id]['lat'] )
      lons.append( st.sts[id]['lon'] )
      gdd50.append(float(row[1]))
      valmask.append( True )
    
    m = MapPlot(title=("Iowa %s thru %s GDD(base=%s,max=%s) Accumulation"
                       "") % (sts.strftime("%Y: %d %b"), 
                              (ets - datetime.timedelta(days=1)).strftime("%d %b"),
                              baseV, maxV),
                axisbg='white')
    m.contourf(lons, lats, gdd50, range(int(min(gdd50)), int(max(gdd50)), 25))
    m.plot_values(lons, lats, gdd50, fmt='%.0f')
    m.drawcounties()
    m.postprocess(web=True)
    m.close()


if __name__ == '__main__':
    main()
