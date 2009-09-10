#!/usr/bin/env python
# Need something to generate a kitchen sink report of Climate Data
# Daryl Herzmann 13 Dec 2004

from constants import *
import sys
from pyIEM import stationTable
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")


def setupCSV(yr):
  out = open("ks/%s_monthly.csv" % (yr,), 'w')
  out.write("stationID,stationName,Latitude,Longitude,")
  for i in range(1,13):
    for v in ["MINT","MAXT","PREC"]:
      out.write("%02i_%s,C%02i_%s," % (i,v,i,v) )
  out.write("%i_MINT,CYR_MINT,%i_MAXT,CYR_MAXT,%i_PREC,CYR_PREC,\n" % (yr,yr,yr) )
  return out

def metadata(id,csv):
  csv.write("%s,%s,%s,%s," % (id, st.sts[id]["name"], st.sts[id]["lat"], \
   st.sts[id]["lon"] ) )

def process(id, csv,yr):
  for i in range(1,13):
    # Compute Climate
    sql = "SELECT round(avg(high)::numeric,1) as avg_high,\
      round(avg(low)::numeric,1) as avg_low, \
      round(sum(precip)::numeric,2) as rain from %s WHERE station = '%s' and \
      extract(month from valid) = %s" % (climatetable(id.lower()), id.lower(), i)
    rs = mydb.query(sql).dictresult()
    aHigh = rs[0]["avg_high"]
    aLow = rs[0]["avg_low"]
    aRain = rs[0]["rain"]

    # Fetch Obs
    sql = "SELECT round(avg_high::numeric,1) as avg_high, \
      round(avg_low::numeric,1) as avg_low, \
      round(rain::numeric,2) as rain from r_monthly WHERE stationid = '%s' \
      and monthdate = '%s-%02i-01'" % (id.lower(), yr, i)
    rs = mydb.query(sql).dictresult()
    oHigh = rs[0]["avg_high"]
    oLow = rs[0]["avg_low"]
    oRain = rs[0]["rain"]

    csv.write("%s,%s,%s,%s,%s,%s," % (oLow,aLow,oHigh,aHigh,oRain,aRain) )

  # Need to do yearly stuff
  # First, get our obs
  sql = "SELECT round(avg(high)::numeric,1) as avg_high,\
      round(avg(low)::numeric,1) as avg_low, \
      round(sum(precip)::numeric,2) as rain from alldata WHERE \
      stationid = '%s' and year = %s " % (id.lower(), yr)
  rs = mydb.query(sql).dictresult()
  oHigh = rs[0]["avg_high"]
  oLow = rs[0]["avg_low"]
  oRain = rs[0]["rain"]
  # Then climate
  sql = "SELECT round(avg(high)::numeric,1) as avg_high,\
    round(avg(low)::numeric,1) as avg_low, \
    round(sum(precip)::numeric,2) as rain from %s WHERE station = '%s' " \
    % (climatetable(id.lower()), id.lower(),)
  rs = mydb.query(sql).dictresult()
  aHigh = rs[0]["avg_high"]
  aLow = rs[0]["avg_low"]
  aRain = rs[0]["rain"]
  csv.write("%s,%s,%s,%s,%s,%s," % (oLow,aLow,oHigh,aHigh,oRain,aRain) )

  csv.write("\n")
  csv.flush()

def main(yr):
  csv = setupCSV(yr)
  for id in st.ids:
    #if (id == 'IA7844' or id == 'IA4381'):
    #  continue
    #if (not longterm.__contains__(id.lower())):
    #  continue
    print "%s processing [%s] %s" % (yr, id, st.sts[id]["name"])
    metadata(id, csv)
    process(id, csv, yr)

if __name__ == "__main__":
  # For what year are we running!
  yr = int(sys.argv[1])
  main(yr)
  #for yr in range(1893,1951):
  #  main(yr)
