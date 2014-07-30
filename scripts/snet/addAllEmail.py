#!/mesonet/python-2.4/bin/python

import pg, sys, traceback
from pyIEM import stationTable
st = stationTable.stationTable("/mesonet/TABLES/kcci.stns")
mydb = pg.connect('kcci')

email = sys.argv[1]
# 
rs = mydb.query("SELECT uid from accounts WHERE email = '%s'" %(email,)).dictresult()

uid = rs[0]['uid']

for sid in st.ids:
  sql = "INSERT into walerts (sid, uid) values ('%s','%s')" % (sid, uid)
  try:
    mydb.query(sql)
  except:
    traceback.print_exc(file=sys.stdout)
