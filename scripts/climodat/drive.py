# This will drive the modules

import pg, string, mx.DateTime
from pyIEM import iemdb
import network
nt = network.Table(('IACLIMATE', 'ILCLIMATE', 'INCLIMATE',
         'OHCLIMATE','MICLIMATE','KYCLIMATE','WICLIMATE','MNCLIMATE',
         'SDCLIMATE','NDCLIMATE','NECLIMATE','KSCLIMATE','MOCLIMATE'))
i = iemdb.iemdb()
mydb = i['coop']

import genPrecipEvents, gen30rains, genGDD, genDailyRecords
import genDailyRecordsRain, genDailyRange, genDailyMeans, genCountLows32
import genSpringFall, genMonthly, genHDD, genCDD, genHeatStress
import genCountRain, genFrostProbabilities, genSpringProbabilities
import genCycles, genCountSnow, genTempThresholds, genRecordPeriods

import constants

DEBUG = 0

for dbid in nt.sts.keys():
#for id in ['IA2364',]:
  print "processing [%s] %s" % (dbid, nt.sts[dbid]["name"])
  rs = mydb.query("""SELECT d.*, c.climoweek from %s d, climoweek c WHERE station = '%s' and 
    day >= '%s-01-01' and d.sday = c.sday ORDER by day ASC""" % (constants.get_table(dbid),
                dbid, constants.startyear(dbid) ) ).dictresult()

  genPrecipEvents.go(mydb, rs, dbid)
  genPrecipEvents.write(mydb, dbid)

  gen30rains.write(mydb, dbid)

  genGDD.go(mydb, rs, dbid)
  genGDD.write(mydb, dbid)

  genDailyRecords.write(mydb, dbid)

  genDailyRecordsRain.write(mydb, dbid)

  genDailyRange.go(mydb, rs, dbid)
  genDailyRange.write(mydb, dbid)

  genDailyMeans.write(mydb, dbid)

  genCountLows32.write(mydb, dbid)

  genSpringFall.write(mydb, rs, dbid, 32, "09")
  genSpringFall.write(mydb, rs, dbid, 30, "10")
  genSpringFall.write(mydb, rs, dbid, 28, "11")
  genSpringFall.write(mydb, rs, dbid, 26, "12")
  genSpringFall.write(mydb, rs, dbid, 24, "13")
 
  genMonthly.go(mydb, dbid)
  genMonthly.write(mydb, dbid)

  genHDD.go(mydb, rs, dbid)
  genHDD.write(mydb, dbid)

  genCDD.go(mydb, rs, dbid)
  genCDD.write(mydb, dbid)

  genHeatStress.write(mydb, dbid)

  genCountRain.write(mydb, dbid)
  genCountSnow.write(mydb, dbid)

  genFrostProbabilities.write(mydb, dbid)
  genSpringProbabilities.write(mydb, dbid)

  genCycles.write(mydb, rs, dbid, 24)

  genTempThresholds.write(mydb, dbid)

  genRecordPeriods.write(mydb, rs, dbid)
