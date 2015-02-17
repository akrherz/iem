"""
 Hard reset the schoolnet gust information at a bit after midnight, this is
 due to complex clock issues, etc
"""

import datetime
import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor()

today = datetime.datetime.now()
sql = """update summary_%s s SET max_gust = 0
    FROM stations t WHERE t.iemid = s.iemid and day = 'TODAY'
    and max_gust_ts < '%s 00:05' and t.network in ('KCCI','KIMT','KELO')""" % (
    today.year, today.strftime("%Y-%m-%d"),)
icursor.execute(sql)
icursor.close()
IEM.close()
