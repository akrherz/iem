# Need something to generate a kitchen sink report of Climate Data
# Daryl Herzmann 13 Dec 2004

import sys, constants
from pyIEM import stationTable
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")


def setupCSV():
  out = open("ks/yearly.csv", 'w')
  out.write("stationID,stationName,Latitude,Longitude,")
  for i in range(1893,constants._ENDYEAR):
    for v in ["MINT","MAXT","PREC"]:
      out.write("%02i_%s," % (i,v) )
  out.write("CYR_MINT,CYR_MAXT,CYR_PREC,\n")
  return out

def metadata(id,csv):
  csv.write("%s,%s,%s,%s," % (id, st.sts[id]["name"], st.sts[id]["lat"], \
   st.sts[id]["lon"] ) )

def process(id, csv):
  # Fetch Yearly Totals
  sql = "SELECT year, round(avg(high)::numeric,1) as avg_high, \
    round(avg(low)::numeric,1) as avg_low, \
    round(sum(precip)::numeric,2) as rain from alldata \
    WHERE stationid = '%s' and year >= %s \
    GROUP by year ORDER by year ASC" % (id.lower(), constants.startyear(id) )
  rs = constants.mydb.query(sql).dictresult()
  data = {}
  for i in range(len(rs)):
    year = int(rs[i]["year"])
    data[year] = {'oHigh': rs[i]["avg_high"], 'oLow': rs[i]["avg_low"], 
                  'oRain': rs[i]["rain"]}

  for i in range(1893, constants._ENDYEAR):
    if (not data.has_key(i)):
      data[i] = {'oHigh': "M", 'oLow': "M", 'oRain': "M"}
    csv.write("%s,%s,%s,"%(data[i]['oLow'],data[i]['oHigh'],data[i]['oRain']))

  # Need to do climate stuff
  # Then climate
  sql = "SELECT round(avg(high)::numeric,1) as avg_high,\
    round(avg(low)::numeric,1) as avg_low, \
    round(sum(precip)::numeric,2) as rain from %s WHERE station = '%s' " \
    % (constants.climatetable(id.lower()), id.lower(),)
  rs = constants.mydb.query(sql).dictresult()
  aHigh = rs[0]["avg_high"]
  aLow = rs[0]["avg_low"]
  aRain = rs[0]["rain"]
  csv.write("%s,%s,%s," % (aLow,aHigh,aRain) )

  csv.write("\n")
  csv.flush()

def main():
  csv = setupCSV()
  for id in st.ids:
    #if (id == 'IA7844' or id == 'IA4381'):
    #  continue
    print "processing [%s] %s" % (id, st.sts[id]["name"])
    metadata(id, csv)
    process(id, csv)

if __name__ == "__main__":
  main()
