# Archive SN GRlevelx files
"""
CREATE TABLE spotternetwork(
  name varchar,
  valid timestamp with time zone);

SELECT addGeometryColumn('spotternetwork', 'geom', 4326, 'POINT', 2);

CREATE TABLE spotternetwork_2010() inherits (spotternetwork);

CREATE INDEX sn_2010_valid_idx on spotternetwork_2010(valid);

GRANT SELECT on spotternetwork_2010 to nobody,apache;
GRANT SELECT on spotternetwork to nobody,apache;

"""

import sys, re, mx.DateTime, pg, urllib2, os
import re
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']


DATAFORM = re.compile(r"""
^Object\:\s+(?P<lat>[\d\.]+),(?P<lon>[\d\.\-]+)\n
(Icon\:\s+\d+,\d+,\d+,\d+,\d+,\n)?
^Icon\:\s+\d+,\d+,\d+,\d+,\d+,"(?P<name>.*),(?P<tstamp>[0-9]{4}\-[0-1][0-9]\-[0-3][0-9]\s[0-2][0-9]\:[0-5][0-9]\:[0-5][0-9])\sUTC,(?P<move>(Heading|STATIONARY))
""", re.VERBOSE | re.MULTILINE )

def todb(data):
    """
    Need something to ingest the data into the spatial database
    """
    gmt = mx.DateTime.gmt()
    data = data.replace("\\n", ",")
    obs = len( re.findall("Object:", data) )
    for m in DATAFORM.finditer( data ):
      obs -= 1
      d = m.groupdict()
      ts = mx.DateTime.strptime(d['tstamp'], '%Y-%m-%d %H:%M:%S')
      if (gmt - ts).hours > 1 or (gmt -ts).hours < -1:
        continue
      sql = """INSERT into spotternetwork_%s(name, valid, geom) VALUES
         (E'%s', '%s+00', 'SRID=4326;POINT(%s %s)')""" % (ts.year, 
         d['name'].replace("'", "''"), d['tstamp'], d['lon'], d['lat'])
      postgis.query( sql )

    if obs != 0:
      print "Failure!"

gmt = mx.DateTime.gmt()
fp = "http://www.spotternetwork.org/feeds/grlevelx.txt"
try:
  data = urllib2.urlopen( fp ).read()
except IOError:
  sys.exit()

o = open("/tmp/sn.txt", 'w')
o.write( data.replace("Title: ", "Title: %s " % (gmt.strftime("%Y%m%d%H%M"),) ))
o.close()

cmd = "/home/ldm/bin/pqinsert -p 'data a %s bogus text/sn/gr_%s.txt txt' /tmp/sn.txt" % (gmt.strftime("%Y%m%d%H%M"), gmt.strftime("%Y%m%d%H%M"))
os.system(cmd)

todb( data )
