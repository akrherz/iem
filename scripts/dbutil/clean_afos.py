"""Clean up some tables that contain bloaty NWS Text Data

called from RUN_2AM.sh
"""

import psycopg2

# Clean AFOS
AFOS = psycopg2.connect(database='afos', host='iemdb')
acursor = AFOS.cursor()

acursor.execute("""
    delete from products WHERE
    entered < ('YESTERDAY'::date - '7 days'::interval) and
    entered > ('YESTERDAY'::date - '31 days'::interval) and
    (pil ~* '^(RR[1-9SA]|ROB|MAV|MET|MTR|MEX|RWR|STO|HML)'
     or pil in ('HPTNCF', 'WTSNCF','WRKTTU','TSTNCF', 'HD3RSA'))
    """)
if acursor.rowcount == 0:
    print 'clean_afos.py found no products older than 7 days?'
acursor.close()
AFOS.commit()

# Clean Postgis
POSTGIS = psycopg2.connect(database='postgis', host='iemdb')
cursor = POSTGIS.cursor()

cursor.execute("""DELETE from text_products where geom is null""")
cursor.close()
POSTGIS.commit()
