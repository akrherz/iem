# Make sure the database server is up!

import pg, os
try:
  pgconn = pg.connect('postgis', 'iemdb')
except:
  os.system("echo 'IEMDB DOWN!' | mail 5154519249@messaging.sprintpcs.com")
