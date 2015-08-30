"""
 Generate the climodat reports, please!  Run from run.sh
"""
import pg
import traceback
import psycopg2.extras

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
import sys

import datetime

mydb = pg.connect('coop', 'iemdb', user='nobody')
pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

update_all = True if datetime.datetime.today().day == 1 else False

runstations = constants.nt.sts.keys()
if len(sys.argv) == 2:
    runstations = [sys.argv[1], ]
    update_all = True


def caller(func, *args):
    ret = func(*args)
    return ret


def run_station(dbid):
    """Actually run for the given station"""
    table = constants.get_table(dbid)
    # print "processing [%s] %s" % (dbid, constants.nt.sts[dbid]["name"])
    sql = """
        SELECT d.*, c.climoweek from %s d, climoweek c
        WHERE station = '%s' and day >= '%s-01-01' and d.sday = c.sday
        and precip is not null and high is not null and low is not null
        ORDER by day ASC
        """ % (table, dbid, constants.startyear(dbid))
    rs = caller(mydb.query, sql).dictresult()

    # Compute monthly
    cursor.execute("""
    SELECT year, month, sum(precip) as sum_precip,
    avg(high) as avg_high,
    avg(low) as avg_low,
    sum(cdd(high,low,60)) as cdd60,
    sum(cdd(high,low,65)) as cdd65,
    sum(hdd(high,low,60)) as hdd60,
    sum(hdd(high,low,65)) as hdd65,
    sum(case when precip >= 0.01 then 1 else 0 end) as rain_days,
    sum(case when snow >= 0.1 then 1 else 0 end) as snow_days,
    sum(gddxx(40,86,high,low)) as gdd40,
    sum(gddxx(48,86,high,low)) as gdd48,
    sum(gddxx(50,86,high,low)) as gdd50,
    sum(gddxx(52,86,high,low)) as gdd52
     from """+table+""" WHERE station = %s GROUP by year, month
    """, (dbid, ))
    monthly_rows = cursor.fetchall()

    out = constants.make_output(constants.nt, dbid, "01")
    caller(genPrecipEvents.write, cursor, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "02")
    caller(gen30rains.write, mydb, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "03")
    caller(genGDD.write, monthly_rows, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "04")
    caller(genDailyRecords.write, mydb, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "05")
    caller(genDailyRecordsRain.write, mydb, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "06")
    caller(genDailyRange.write, mydb, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "07")
    caller(genDailyMeans.write, mydb, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "08")
    caller(genCountLows32.write, cursor, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "09")
    caller(genSpringFall.write, out, rs, dbid, 32)
    out.close()

    out = constants.make_output(constants.nt, dbid, "10")
    caller(genSpringFall.write, out, rs, dbid, 30)
    out.close()

    out = constants.make_output(constants.nt, dbid, "11")
    caller(genSpringFall.write, out, rs, dbid, 28)
    out.close()

    out = constants.make_output(constants.nt, dbid, "12")
    caller(genSpringFall.write, out, rs, dbid, 26)
    out.close()

    out = constants.make_output(constants.nt, dbid, "13")
    caller(genSpringFall.write, out, rs, dbid, 24)
    out.close()

    out = constants.make_output(constants.nt, dbid, "14")
    out2 = constants.make_output(constants.nt, dbid, "15")
    out3 = constants.make_output(constants.nt, dbid, "16")
    out4 = constants.make_output(constants.nt, dbid, "17")
    caller(genMonthly.write, monthly_rows, out, out2, out3, out4, dbid)
    out.close()
    out2.close()
    out3.close()
    out4.close()

    out = constants.make_output(constants.nt, dbid, "18")
    caller(genHDD.write, monthly_rows, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "19")
    caller(genCDD.write, monthly_rows, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "20")
    caller(genHeatStress.write, cursor, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "21")
    caller(genCountRain.write, monthly_rows, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "25")
    caller(genCountSnow.write, monthly_rows, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "22")
    caller(genFrostProbabilities.write, mydb, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "23")
    caller(genSpringProbabilities.write, cursor, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "24")
    caller(genCycles.write, out, rs, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "26")
    caller(genTempThresholds.write, cursor, out, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "27")
    caller(genRecordPeriods.write, mydb, out, rs, dbid)
    out.close()

    out = constants.make_output(constants.nt, dbid, "28")
    caller(gen_precip_cats.write, mydb, out, rs, dbid)
    out.close()


def main():
    for dbid in runstations:
        try:
            run_station(dbid)
        except:
            print 'climodat/drive.py failure for %s' % (dbid, )
            print traceback.print_exc()
            sys.exit()

if __name__ == '__main__':
    main()
