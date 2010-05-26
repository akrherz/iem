
import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']
iem.query("SET TIME ZONE 'GMT'")

  # Our period
t0 = mx.DateTime.utc() + mx.DateTime.RelativeDateTime(hours=-1,minute=0)
t1 = mx.DateTime.utc() + mx.DateTime.RelativeDateTime(hours=-0,minute=0)

sql = "INSERT into hourly_%s \
       (SELECT station, network, '%s+00'::timestamp as v, max(phour) as p \
        from current_log WHERE (valid - '1 minute'::interval) >= '%s' \
        and (valid - '1 minute'::interval) < '%s' and phour >= 0 and \
        network NOT IN ('KCCI','KELO','KIMT') GROUP by station, network, v)" % \
       (t0.year, t0.strftime("%Y-%m-%d %H:%M"), t0.strftime("%Y-%m-%d %H:%M"), \
        t1.strftime("%Y-%m-%d %H:%M") )
iem.query( sql )
