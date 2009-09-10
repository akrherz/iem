#!/mesonet/python/bin/python
# Dump entire COOP archive to CSV files

from pyIEM import stationTable, iemdb
i = iemdb.iemdb()
coop = i['coop']

st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")

for id in st.ids:
  fn = "coop_data/%s.csv" % (st.sts[id]['name'].replace(" ", "_"), )
  out = open(fn, 'w')
  out.write("station,station_name,lat,lon,day,high,low,precip,snow,\n")
  sql = "SELECT * from alldata WHERE stationid = '%s' ORDER by day ASC" \
         % (id.lower(), )

  rs = coop.query(sql).dictresult()
  for i in range(len(rs)):
    out.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,\n" % (id.lower(), st.sts[id]['name'], st.sts[id]['lat'], st.sts[id]['lon'],\
       rs[i]['day'], rs[i]['high'], rs[i]['low'], rs[i]['precip'], rs[i]['snow']) )

  out.close()
