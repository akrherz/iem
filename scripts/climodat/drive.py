"""
 Generate the climodat reports, please!  Run from run.sh
"""

import pg
import network
nt = network.Table(('IACLIMATE', 'ILCLIMATE', 'INCLIMATE',
         'OHCLIMATE','MICLIMATE','KYCLIMATE','WICLIMATE','MNCLIMATE',
         'SDCLIMATE','NDCLIMATE','NECLIMATE','KSCLIMATE','MOCLIMATE'))
mydb = pg.connect('coop', 'iemdb', user='nobody')

import genPrecipEvents
import gen30rains
import genGDD
import genDailyRecords
import genDailyRecordsRain
import genDailyRange
import genDailyMeans
import genCountLows32
import genSpringFall
import genMonthly
import genHDD
import genCDD
import genHeatStress
import genCountRain
import genFrostProbabilities
import genSpringProbabilities
import genCycles
import genCountSnow
import genTempThresholds
import genRecordPeriods
import gen_precip_cats

import constants

DEBUG = 0
updateAll= False
for dbid in nt.sts.keys():
    #print "processing [%s] %s" % (dbid, nt.sts[dbid]["name"])
    rs = mydb.query("""SELECT d.*, c.climoweek from %s d, climoweek c 
    WHERE station = '%s' and day >= '%s-01-01' and d.sday = c.sday 
    ORDER by day ASC""" % (constants.get_table(dbid),
                dbid, constants.startyear(dbid) ) ).dictresult()

    genPrecipEvents.go(mydb, rs, dbid)
    out = constants.make_output(nt, dbid, "01")
    genPrecipEvents.write(mydb, out, dbid)
    out.close()

    out = constants.make_output(nt, dbid, "02")
    gen30rains.write(mydb, out, dbid)
    out.close()
    
    genGDD.go(mydb, rs, dbid, updateAll)
    out = constants.make_output(nt, dbid, "03")
    genGDD.write(mydb, out, dbid)
    out.close()

    out = constants.make_output(nt, dbid, "04")
    genDailyRecords.write(mydb, out, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "05")
    genDailyRecordsRain.write(mydb, out, dbid)
    out.close()
    
    #genDailyRange.go(mydb, rs, dbid)
    out = constants.make_output(nt, dbid, "06")
    genDailyRange.write(mydb, out, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "07")
    genDailyMeans.write(mydb, out, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "08")
    genCountLows32.write(mydb, out, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "09")
    genSpringFall.write(mydb, out, rs, dbid, 32)
    out.close()
    
    out = constants.make_output(nt, dbid, "10")
    genSpringFall.write(mydb, out, rs, dbid, 30)
    out.close()
    
    out = constants.make_output(nt, dbid, "11")
    genSpringFall.write(mydb, out, rs, dbid, 28)
    out.close()
    
    out = constants.make_output(nt, dbid, "12")
    genSpringFall.write(mydb, out, rs, dbid, 26)
    out.close()
    
    out = constants.make_output(nt, dbid, "13")
    genSpringFall.write(mydb, out, rs, dbid, 24)
    out.close()
    
    genMonthly.go(mydb, dbid, updateAll)
    out = constants.make_output(nt, dbid, "14")
    out2 = constants.make_output(nt, dbid, "15")
    out3 = constants.make_output(nt, dbid, "16")
    out4 = constants.make_output(nt, dbid, "17")
    genMonthly.write(mydb, out, out2, out3, out4, dbid)
    out.close()
    out2.close()
    out3.close()
    out4.close()
    
    genHDD.go(mydb, rs, dbid, updateAll)
    out = constants.make_output(nt, dbid, "18")
    genHDD.write(mydb, out, dbid)
    out.close()
    
    genCDD.go(mydb, rs, dbid, updateAll)
    out = constants.make_output(nt, dbid, "19")
    genCDD.write(mydb, out, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "20")
    genHeatStress.write(mydb, out, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "21")
    genCountRain.write(mydb, out, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "25")
    genCountSnow.write(mydb, out, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "22")
    genFrostProbabilities.write(mydb, out, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "23")
    genSpringProbabilities.write(mydb, out, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "24")
    genCycles.write(mydb, out, rs, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "26")
    genTempThresholds.write(mydb, out, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "27")
    genRecordPeriods.write(mydb, out, rs, dbid)
    out.close()
    
    out = constants.make_output(nt, dbid, "28")
    gen_precip_cats.write(mydb, out, rs, dbid)
    out.close()
    
