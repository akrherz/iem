
import os
from pyIEM import iemdb, mesonet
i = iemdb.iemdb()
mesosite = i['mesosite']
import glob

os.chdir("work")
files = glob.glob("*640x480.jpg")
for file in files:
  cid = file[:11]

  rs = mesosite.query("SELECT * from webcams WHERE id = '%s'" % (cid,)).dictresult()
  if len(rs) > 0:
    continue

  rid = cid[6:8]
  nwsli = mesonet.RWISconvert[ rid ]

  rs = mesosite.query("SELECT name, x(geom) as lon, y(geom) as lat from stations where id = '%s'" % (nwsli,)).dictresult()
  lon = rs[0]['lon']
  lat = rs[0]['lat']
  name = rs[0]['name']
  print 'Adding %s name [%s] lon [%s] lat [%s]' % (cid, name, lon, lat)
  sql = """insert into webcams (sts, id, name, pan0, online, network, 
         geom, removed, state) values (now(), '%s', '%s', 0, 't', 'IDOT', 'SRID=4326;POINT(%s %s)', 'f', 'IA')""" % (cid, name, lon, lat)
  mesosite.query( sql )

