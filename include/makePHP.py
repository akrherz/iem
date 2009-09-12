#!/mesonet/python/bin/python

from pyIEM import iemdb
import mx.DateTime
i = iemdb.iemdb()
mesosite = i['mesosite']

rs = mesosite.query("SELECT *, x(geom), y(geom), case when removed then 'True' else 'False' end as r, case when online then 'True' else 'False' end as c from webcams  ORDER by name ASC").dictresult()

o = open('cameras.inc.php', 'w')
o.write("""<?php
$cameras = Array(
""");

for i in range(len(rs)):
  sts = mx.DateTime.strptime(rs[i]['sts'][:16], '%Y-%m-%d %H:%M')
  estr = "time()"
  if (rs[i]['ets'] is not None):
    ets = mx.DateTime.strptime(rs[i]['ets'][:16], '%Y-%m-%d %H:%M')
    estr = "mktime(%s,0,0,%s, %s,%s)" % (ets.hour, ets.month, ets.day, ets.year)

  o.write(""""%s" => Array("sts" => mktime(%s,0,0,%s, %s,%s), "ets" => %s,
    "name" => "%s", "removed" => %s, "active" => %s, "lat" => %s, "lon" => %s,
    "state" => "%s", "network" => "%s", "moviebase" => "%s",
    "ip" => "%s", "county" => "%s", "port" => "%s"),\n""" \
   % (rs[i]['id'], sts.hour, sts.month, sts.day, sts.year, estr, \
      rs[i]['name'], rs[i]['r'], rs[i]['c'], rs[i]['y'], rs[i]['x'], \
      rs[i]['state'], rs[i]['network'], rs[i]['moviebase'], \
      rs[i]['ip'], rs[i]['county'], \
      rs[i]['port']) )

o.write("""); ?>""")
o.close()
