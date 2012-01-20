from metar import Metar
import iemdb

IEM = iemdb.connect("iem", bypass=True)
icursor = IEM.cursor()
icursor2 = IEM.cursor()

icursor.execute("""
  select valid, c.iemid, raw from current_log c JOIN stations s 
  on (s.iemid = c.iemid) and s.network ~* 'ASOS' 
""")
total = 0
for row in icursor:
    try:
        mtr = Metar.Metar(row[2], row[0].month, row[0].year)
    except:
        #print 'Error', row
        continue
    sql = 'update current_log SET '
    if mtr.max_temp_6hr:
        sql += "max_tmpf_6hr = %s," % (mtr.max_temp_6hr.value("F"),)
    if mtr.min_temp_6hr:
        sql += "min_tmpf_6hr = %s," % (mtr.min_temp_6hr.value("F"),)
    if mtr.max_temp_24hr:
        sql += "max_tmpf_24hr = %s," % (mtr.max_temp_24hr.value("F"),)
    if mtr.min_temp_24hr: 
        sql += "min_tmpf_24hr = %s," % (mtr.min_temp_24hr.value("F"),)
    if mtr.precip_3hr:
        sql += "p03i = %s," % (mtr.precip_3hr.value("IN"),)
    if mtr.precip_6hr:
        sql += "p06i = %s," % (mtr.precip_6hr.value("IN"),)
    if mtr.precip_24hr:
        sql += "p24i = %s," % (mtr.precip_24hr.value("IN"),)
    if mtr.press_sea_level:
        sql += "pres = %s," % (mtr.press_sea_level.value("MB"),)
    if mtr.weather:
        pwx = []
        for x in mtr.weather:
            pwx.append( ("").join([a for a in x if a is not None]) )
        sql += "presentwx = '%s'," % ((",".join(pwx))[:24], )
    if sql == "update current_log SET ":
        continue
    sql = "%s WHERE iemid = %s and valid = '%s'" % (sql[:-1], row[1],
                                                    row[0])
    #print sql
    icursor2.execute(sql)
    total += 1 
    if total % 1000 == 0:
        print 'Done', total
        IEM.commit()
icursor2.close()
IEM.commit()
IEM.close()
