# 11 Feb 2005	Fix update of summary table

import mx.DateTime
from pyIEM import iemAccess
iemaccess = iemAccess.iemAccess()

today = mx.DateTime.now()
if today.hour == 0:
  iemaccess.query("""update summary_%s SET max_gust = 0 \
    WHERE day = 'TODAY' and max_gust_ts < '%s 00:05' and
    network in ('KCCI','KIMT','KELO')""" % (
    today.year, today.strftime("%Y-%m-%d"),) )
