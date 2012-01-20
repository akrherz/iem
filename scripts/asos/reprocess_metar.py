from metar import Metar
import iemdb, mx.DateTime

IEM = iemdb.connect("asos", bypass=True)
icursor = IEM.cursor()
icursor.execute("SET TIME ZONE 'GMT'")
icursor2 = IEM.cursor()

sts = mx.DateTime.DateTime(2011,1,1)
ets = mx.DateTime.DateTime(2012,1,1)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
while now < ets:
    icursor.execute("""
  select valid, station, metar from t%s 
  where metar is not null and valid >= '%s' and valid < '%s'
    """ % (now.year, now.strftime("%Y-%m-%d"), 
    (now+interval).strftime("%Y-%m-%d")))
    total = 0
    for row in icursor:
        try:
            mtr = Metar.Metar(row[2], row[0].month, row[0].year)
        except:
            #print 'Error', row
            continue
        sql = 'update t%s SET ' % (now.year,)
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
            sql += "mslp = %s," % (mtr.press_sea_level.value("MB"),)
        if mtr.weather:
            pwx = []
            for x in mtr.weather:
                pwx.append( ("").join([a for a in x if a is not None]) )
            sql += "presentwx = '%s'," % ((",".join(pwx))[:24], )
        if sql == "update t%s SET " % (now.year,):
            continue
        sql = "%s WHERE station = '%s' and valid = '%s'" % (sql[:-1], row[1],
                                                    row[0])
        #print sql
        icursor2.execute(sql)
        total += 1 
        if total % 1000 == 0:
            print 'Done', total, now
            IEM.commit()
    now += interval
icursor2.close()
IEM.commit()
IEM.close()
