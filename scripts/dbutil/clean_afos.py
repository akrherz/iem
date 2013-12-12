"""
 Clean up the AFOS database
    called from RUN_2AM.sh
"""

import psycopg2
AFOS = psycopg2.connect(database='afos', host='iemdb')
acursor = AFOS.cursor()

acursor.execute("""
 delete from products WHERE 
   entered < ('YESTERDAY'::date - '7 days'::interval) and
   entered > ('YESTERDAY'::date - '31 days'::interval) and 
   (
    pil ~* '^(RR[1-9SA]|ROB|TAF|MAV|MET|MTR|MEX|RWR|STO|HML)' 
 or pil in ('HPTNCF', 'WTSNCF','WRKTTU','TSTNCF', 'HD3RSA')
   )""")
if acursor.rowcount == 0:
    print 'clean_afos.py found no products older than 7 days?'
acursor.close()
AFOS.commit()
