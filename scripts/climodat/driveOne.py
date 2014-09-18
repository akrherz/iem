# This will drive the modules

import pg
import string
import constants
import datetime
import network
nt = network.Table("IACLIMATE")
mydb = pg.connect("coop", 'iemdb',user='nobody')

import genPrecipEvents,  genGDD, genDailyRecords
import genDailyRecordsRain, genDailyRange, genDailyMeans, genCountLows32
import genSpringFall, genMonthly, genHDD, genCDD, genHeatStress
import genCountRain, genFrostProbabilities, genSpringProbabilities, genCycles
import genTempThresholds, genRecordPeriods, gen_precip_cats

def caller(func, *args):
    #start = datetime.datetime.now()
    ret = func(*args)
    #end = datetime.datetime.now()
    #print "%s %s took %s" % (func.__name__, args[-1], (end-start))
    return ret
update_all = True 

#for id in st.ids:
for id in ['IA0200',]:
    print "processing [%s] %s" % (id, nt.sts[id]["name"])
    dbid = string.upper(id)
    rs = mydb.query("""SELECT * from %s WHERE station = '%s' and 
    day >= '%s-01-01' ORDER by day ASC""" % (
    constants.get_table(dbid), dbid, constants.startyear(dbid) ) ).dictresult()
    #genSpringFall.write(mydb, rs, dbid, 32, "09")
    #genHDD.go(mydb, rs, dbid, updateAll)
    #genHDD.write(mydb, dbid)
    
    caller(genMonthly.go, mydb, dbid, update_all)
    out = caller(constants.make_output, nt, dbid, "14")
    out2 = caller(constants.make_output, nt, dbid, "15")
    out3 = caller(constants.make_output, nt, dbid, "16")
    out4 = caller(constants.make_output, nt, dbid, "17")
    caller(genMonthly.write,mydb, out, out2, out3, out4, dbid)
    out.close()
    out2.close()
    out3.close()
    out4.close()