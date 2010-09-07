# This will drive the modules

import pg, string, mx.DateTime
from pyIEM import stationTable, iemdb
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
i = iemdb.iemdb()
mydb = i['coop']

import genPrecipEvents, gen30rains, genGDD, genDailyRecords
import genDailyRecordsRain, genDailyRange, genDailyMeans, genCountLows32
import genSpringFall, genMonthly, genHDD, genCDD, genHeatStress
import genCountRain, genFrostProbabilities, genSpringProbabilities
import genCycles, genCountSnow, genTempThresholds, genRecordPeriods

import constants

DEBUG = 0


for id in st.ids:
#for id in ['IA2364',]:
  print "processing [%s] %s" % (id, st.sts[id]["name"])
  dbid = string.lower(id)
  if DEBUG: print "Query all data", mx.DateTime.now()
  rs = mydb.query("SELECT * from alldata WHERE stationid = '%s' and \
    day >= '%s-01-01' ORDER by day ASC" \
    % (dbid, constants.startyear(dbid) ) ).dictresult()

  if DEBUG: print "genPrecipEvents", mx.DateTime.now()
  genPrecipEvents.go(mydb, rs, dbid)
  genPrecipEvents.write(mydb, dbid)

  if DEBUG: print "gen30rains", mx.DateTime.now()
  gen30rains.write(mydb, dbid)

  if DEBUG: print "genGDD", mx.DateTime.now()
  genGDD.go(mydb, rs, dbid)
  genGDD.write(mydb, dbid)

  if DEBUG: print "genDailyRecords", mx.DateTime.now()
  genDailyRecords.write(mydb, dbid)

  if DEBUG: print "genDailyRecordsRain", mx.DateTime.now()
  genDailyRecordsRain.write(mydb, dbid)

  if DEBUG: print "genDailyRange", mx.DateTime.now()
  genDailyRange.go(mydb, rs, dbid)
  genDailyRange.write(mydb, dbid)

  if DEBUG: print "genDailyMeans", mx.DateTime.now()
  genDailyMeans.write(mydb, dbid)

  if DEBUG: print "genCountLows32", mx.DateTime.now()
  genCountLows32.write(mydb, dbid)

  if DEBUG: print "genSpringFall", mx.DateTime.now()
  genSpringFall.write(mydb, rs, dbid, 32, "09")
  genSpringFall.write(mydb, rs, dbid, 30, "10")
  genSpringFall.write(mydb, rs, dbid, 28, "11")
  genSpringFall.write(mydb, rs, dbid, 26, "12")
  genSpringFall.write(mydb, rs, dbid, 24, "13")
 
  if DEBUG: print "genMonthly", mx.DateTime.now()
  genMonthly.go(mydb, dbid)
  genMonthly.write(mydb, dbid)

  if DEBUG: print "genHDD", mx.DateTime.now()
  genHDD.go(mydb, rs, dbid)
  genHDD.write(mydb, dbid)

  if DEBUG: print "genCDD", mx.DateTime.now()
  genCDD.go(mydb, rs, dbid)
  genCDD.write(mydb, dbid)

  if DEBUG: print "genHeatStress", mx.DateTime.now()
  genHeatStress.write(mydb, dbid)

  if DEBUG: print "genCountRain", mx.DateTime.now()
  genCountRain.write(mydb, dbid)
  genCountSnow.write(mydb, dbid)

  if DEBUG: print "genFrostProbabilities", mx.DateTime.now()
  genFrostProbabilities.write(mydb, dbid)
  if DEBUG: print "genSpringProbabilities", mx.DateTime.now()
  genSpringProbabilities.write(mydb, dbid)

  if DEBUG: print "genCycles", mx.DateTime.now()
  genCycles.write(mydb, rs, dbid, 24)

  if DEBUG: print "genTempThresholds", mx.DateTime.now()
  genTempThresholds.write(mydb, dbid)

  if DEBUG: print "genRecordPeriods", mx.DateTime.now()
  genRecordPeriods.write(mydb, rs, dbid)
