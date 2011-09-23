# This will drive the modules

import pg, string, constants
import network
nt = network.Table("IACLIMATE")
mydb = pg.connect("coop", 'iemdb',user='nobody')

import genPrecipEvents, genTwelveRains, genGDD, genDailyRecords
import genDailyRecordsRain, genDailyRange, genDailyMeans, genCountLows32
import genSpringFall, genMonthly, genHDD, genCDD, genHeatStress
import genCountRain, genFrostProbabilities, genSpringProbabilities, genCycles
import genTempThresholds, genRecordPeriods

#for id in st.ids:
for id in ['IA0200',]:
  print "processing [%s] %s" % (id, nt.sts[id]["name"])
  dbid = string.lower(id)
  rs = mydb.query("SELECT * from %s WHERE station = '%s' and \
    day >= '%s-01-01' ORDER by day ASC" \
    % (dbid, constants.get_table(dbid), constants.startyear(dbid) ) ).dictresult()
  #genSpringFall.write(mydb, rs, dbid, 32, "09")
  #genSpringFall.write(mydb, rs, dbid, 30, "10")
  #genSpringFall.write(mydb, rs, dbid, 28, "11")
  #genSpringFall.write(mydb, rs, dbid, 26, "12")
  #genSpringFall.write(mydb, rs, dbid, 24, "13")

  #genMonthly.write(mydb, dbid)
  genRecordPeriods.write(mydb, rs, dbid)
