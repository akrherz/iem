#!/mesonet/python/bin/python
# This will drive the modules

import pg, string, constants
from pyIEM import stationTable
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
mydb = pg.connect("coop", 'iemdb')

import genPrecipEvents, genTwelveRains, genGDD, genDailyRecords
import genDailyRecordsRain, genDailyRange, genDailyMeans, genCountLows32
import genSpringFall, genMonthly, genHDD, genCDD, genHeatStress
import genCountRain, genFrostProbabilities, genSpringProbabilities, genCycles

for id in st.ids:
#for id in ['IA1319',]:
  print "processing [%s] %s" % (id, st.sts[id]["name"])
  dbid = string.lower(id)
  #rs = mydb.query("SELECT * from alldata WHERE stationid = '%s' and \
  #  day >= '%s-01-01' ORDER by day ASC" \
  #  % (dbid, constants.startyear(dbid) ) ).dictresult()

  genMonthly.write(mydb, dbid)
