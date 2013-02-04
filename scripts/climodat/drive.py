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


#stdlib
import datetime

def caller(func, *args):
    #start = datetime.datetime.now()
    ret = func(*args)
    #end = datetime.datetime.now()
    #print "%s %s took %s" % (func.__name__, args[-1], (end-start))
    return ret

updateAll= False
for dbid in nt.sts.keys():
    #print "processing [%s] %s" % (dbid, nt.sts[dbid]["name"])
    sql = """SELECT d.*, c.climoweek from %s d, climoweek c 
    WHERE station = '%s' and day >= '%s-01-01' and d.sday = c.sday 
    ORDER by day ASC""" % (constants.get_table(dbid),
                dbid, constants.startyear(dbid) ) 

    rs = caller(mydb.query, sql).dictresult()

    caller(genPrecipEvents.go, mydb, rs, dbid)
    out = caller(constants.make_output, nt, dbid, "01")
    caller(genPrecipEvents.write, mydb, out, dbid)
    out.close()

    out = caller(constants.make_output, nt, dbid, "02")
    caller(gen30rains.write, mydb, out, dbid)
    out.close()
    
    caller(genGDD.go, mydb, rs, dbid, updateAll)
    out = caller(constants.make_output, nt, dbid, "03")
    caller(genGDD.write, mydb, out, dbid)
    out.close()

    out = caller(constants.make_output, nt, dbid, "04")
    caller(genDailyRecords.write, mydb, out, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "05")
    caller(genDailyRecordsRain.write, mydb, out, dbid)
    out.close()
    
    #genDailyRange.go(mydb, rs, dbid)
    out = caller(constants.make_output, nt, dbid, "06")
    caller(genDailyRange.write, mydb, out, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "07")
    caller(genDailyMeans.write, mydb, out, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "08")
    caller(genCountLows32.write, mydb, out, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "09")
    caller(genSpringFall.write, mydb, out, rs, dbid, 32)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "10")
    caller(genSpringFall.write, mydb, out, rs, dbid, 30)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "11")
    caller(genSpringFall.write, mydb, out, rs, dbid, 28)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "12")
    caller(genSpringFall.write, mydb, out, rs, dbid, 26)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "13")
    caller(genSpringFall.write, mydb, out, rs, dbid, 24)
    out.close()
    
    caller(genMonthly.go, mydb, dbid, updateAll)
    out = caller(constants.make_output, nt, dbid, "14")
    out2 = caller(constants.make_output, nt, dbid, "15")
    out3 = caller(constants.make_output, nt, dbid, "16")
    out4 = caller(constants.make_output, nt, dbid, "17")
    caller(genMonthly.write,mydb, out, out2, out3, out4, dbid)
    out.close()
    out2.close()
    out3.close()
    out4.close()
    
    caller(genHDD.go, mydb, rs, dbid, updateAll)
    out = caller(constants.make_output, nt, dbid, "18")
    caller(genHDD.write, mydb, out, dbid)
    out.close()
    
    caller(genCDD.go, mydb, rs, dbid, updateAll)
    out = caller(constants.make_output, nt, dbid, "19")
    caller(genCDD.write, mydb, out, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "20")
    genHeatStress.write(mydb, out, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "21")
    caller(genCountRain.write, mydb, out, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "25")
    caller(genCountSnow.write, mydb, out, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "22")
    caller(genFrostProbabilities.write, mydb, out, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "23")
    caller(genSpringProbabilities.write, mydb, out, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "24")
    caller(genCycles.write, mydb, out, rs, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "26")
    caller(genTempThresholds.write, mydb, out, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "27")
    caller(genRecordPeriods.write, mydb, out, rs, dbid)
    out.close()
    
    out = caller(constants.make_output, nt, dbid, "28")
    caller(gen_precip_cats.write, mydb, out, rs, dbid)
    out.close()
    
