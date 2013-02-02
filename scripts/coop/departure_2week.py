"""
Generate a report for 2 week precip departures
"""
from xlwt import Workbook
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import network
nt = network.Table("IACLIMATE")

ccursor.execute("""
select obs.station, obs.sum, climate.sum from 
  (select station, sum(precip) from alldata_ia where 
  day >= '2012-05-16' and day < '2012-05-30' GROUP by station) as obs, 
  (SELECT station, sum(precip) from climate51 
  WHERE valid >= '2000-05-16' and valid < '2000-05-30' GROUP by station) as climate 
  WHERE climate.station = obs.station and climate.station NOT IN
  ('IA0000', 'IAC0001', 'IAC0002','IAC0003','IAC0004','IAC0005','IAC0006',
  'IAC0007','IAC0008','IAC0009')
""")

book = Workbook()
sheet = book.add_sheet('data')
row = sheet.row(0)
row.write(0, "ID")
row.write(1, "LONGITUDE")
row.write(2, "LATITUDE")
row.write(3, "OBS_PREC_IN")
row.write(4, "CLIM_PREC_IN")
row.write(5, "PRECENTAGE")
i = 1
for row in ccursor:
    if not nt.sts.has_key(row[0]):
        continue
    row2 = sheet.row(i)
    row2.write(0, row[0])
    row2.write(1, nt.sts[row[0]]['lon'])
    row2.write(2, nt.sts[row[0]]['lat'])
    row2.write(3, row[1])
    row2.write(4, row[2])
    row2.write(5, row[1] / row[2] * 100.0)
    i += 1
    
book.save('test.xls')
