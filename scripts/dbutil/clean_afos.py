# Clean up the AFOS database

import pg, mx.DateTime
afos = pg.connect('afos', 'iemdb')

now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=7)
table = "products_%s_" % (now.year,)
if now.month > 6:
  table += "0712"
else:
  table += "0106"

table = "products"

sql = """
 delete from %s WHERE 
   date(entered) < ('YESTERDAY'::date - '7 days'::interval) and
   (pil ~* '^(RR[1-9SA]|ROB|TAF|MAV|MET|MTR|MEX|RWR|STO|HML)' 
    or pil in ('HPTNCF', 'WTSNCF','WRKTTU')
   )""" % (table,)
afos.query( sql )