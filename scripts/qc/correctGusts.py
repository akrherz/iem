# 11 Feb 2005	Fix update of summary table

import mx.DateTime
import iemdb
IEM = iemdb.connect('iem')
icursor = IEM.cursor()

today = mx.DateTime.now()
sql = """update summary_%s SET max_gust = 0 
    WHERE day = 'TODAY' and max_gust_ts < '%s 00:05' and
    network in ('KCCI','KIMT','KELO')""" % (
    today.year, today.strftime("%Y-%m-%d"),)
icursor.execute(sql)
icursor.close()
IEM.close()
