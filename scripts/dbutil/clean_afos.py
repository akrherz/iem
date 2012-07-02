"""
 Clean up the AFOS database
"""

import iemdb, mx.DateTime
AFOS = iemdb.connect('afos')
acursor = AFOS.cursor()

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
    or pil in ('HPTNCF', 'WTSNCF','WRKTTU','TSTNCF', 'HD3RSA')
   )""" % (table,)
acursor.execute( sql )
acursor.close()
AFOS.commit()
