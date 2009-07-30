# Generate maps of Average Temperatures

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb, stationTable
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
st.sts["IA0200"]["lon"] = -93.4
st.sts["IA5992"]["lat"] = 41.65
i = iemdb.iemdb()
coop = i['coop']

def runYear(year):
  # Grab the data
  sql = """SELECT stationid, avg(high) as avg_high, avg(low) as avg_low,
           avg( (high+low)/2 ) as avg_tmp
           from alldata WHERE year = %s GROUP by stationid""" % (year,)
  rs = coop.query(sql).dictresult()

  # Plot Average Highs
  lats = []
  lons = []
  vals = []
  labels = []
  for i in range(len(rs)):
    id = rs[i]['stationid'].upper()
    if not st.sts.has_key(id):
      continue
    labels.append( id[2:] )
    lats.append( st.sts[id]['lat'] )
    lons.append( st.sts[id]['lon'] )
    vals.append( rs[i]['avg_high'] )

    #---------- Plot the points

  cfg = {
     'wkColorMap': 'gsltod',
     '_format'   : '%.1f',
     '_labels'   : labels,
     '_title'    : "Average Daily High Temperature [F] (%s)" % (year,),
  }

  iemplot.simple_valplot(lons, lats, vals, cfg)

  os.system("convert -depth 8 -colors 128 -trim -border 5 -bordercolor '#fff' -resize 900x700 +repage -density 120 tmp.ps temp.png")
  os.system("/home/ldm/bin/pqinsert -p 'plot m %s/summary/avg_high.png' temp.png" % (year,))
  os.remove("temp.png")
  os.remove("tmp.ps")

  # Plot Average Lows
  lats = []
  lons = []
  vals = []
  labels = []
  for i in range(len(rs)):
    id = rs[i]['stationid'].upper()
    if not st.sts.has_key(id):
      continue
    labels.append( id[2:] )
    lats.append( st.sts[id]['lat'] )
    lons.append( st.sts[id]['lon'] )
    vals.append( rs[i]['avg_low'] )

    #---------- Plot the points

  cfg = {
     'wkColorMap': 'gsltod',
     '_format'   : '%.1f',
     '_labels'   : labels,
     '_title'    : "Average Daily Low Temperature [F] (%s)" % (year,),
  }

  iemplot.simple_valplot(lons, lats, vals, cfg)

  os.system("convert -depth 8 -colors 128 -trim -border 5 -bordercolor '#fff' -resize 900x700 +repage -density 120 tmp.ps temp.png")
  os.system("/home/ldm/bin/pqinsert -p 'plot m %s/summary/avg_low.png' temp.png" % (year,))
  os.remove("temp.png")
  os.remove("tmp.ps")

  # Plot Average Highs
  lats = []
  lons = []
  vals = []
  labels = []
  for i in range(len(rs)):
    id = rs[i]['stationid'].upper()
    if not st.sts.has_key(id):
      continue
    labels.append( id[2:] )
    lats.append( st.sts[id]['lat'] )
    lons.append( st.sts[id]['lon'] )
    vals.append( rs[i]['avg_high'] )

    #---------- Plot the points

  cfg = {
     'wkColorMap': 'gsltod',
     '_format'   : '%.1f',
     '_labels'   : labels,
     '_title'    : "Average Daily Temperature (mean high+low) [F] (%s)" % (year,),
  }

  iemplot.simple_valplot(lons, lats, vals, cfg)

  os.system("convert -depth 8 -colors 128 -trim -border 5 -bordercolor '#fff' -resize 900x700 +repage -density 120 tmp.ps temp.png")
  os.system("/home/ldm/bin/pqinsert -p 'plot m %s/summary/avg_temp.png' temp.png" % (year,))
  os.remove("temp.png")
  os.remove("tmp.ps")


if __name__ == '__main__':
  runYear( sys.argv[1] )
