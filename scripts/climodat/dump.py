import constants
from pyIEM import iemdb
import network
nt = network.Table("IACLIMATE")
i = iemdb.iemdb()
coop = i['coop']

for id in nt.sts.keys():
  fn = "coop_data/%s.csv" % (st.sts[id]['name'].replace(" ", "_"), )
  out = open(fn, 'w')
  out.write("station,station_name,lat,lon,day,high,low,precip,snow,\n")
  sql = "SELECT * from %s WHERE station = '%s' ORDER by day ASC" \
         % (constants.get_table(id), id.lower(), )

  rs = coop.query(sql).dictresult()
  for i in range(len(rs)):
    out.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,\n" % (id.lower(), st.sts[id]['name'], st.sts[id]['lat'], st.sts[id]['lon'],\
       rs[i]['day'], rs[i]['high'], rs[i]['low'], rs[i]['precip'], rs[i]['snow']) )

  out.close()
