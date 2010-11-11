import mx.DateTime
from pyIEM import iemdb 
i = iemdb.iemdb()
asos = i['asos']

# Extract daily stats
rs = asos.query("""SELECT date(valid) as d, 
  sum( case when skyc1 in ('BKN','OVC') or skyc2 in ('BKN','OVC') or skyc3 in ('BKN','OVC') then 1 else 0 end ) as clouds
  from alldata where 
  station = 'DVN' and tmpf > -50 and sknt >= 0 and valid > '1950-01-01' 
  and extract(hour from valid) > 5 and extract(hour from valid) < 18 GROUP by d
  ORDER by d ASC""").dictresult()
cnt = [0]*366
running = 0
for i in range(len(rs)):
  ts =  mx.DateTime.strptime( rs[i]['d'], '%Y-%m-%d')
  if rs[i]['clouds'] < 3:
    running += 1
    ts -= mx.DateTime.RelativeDateTime(days=1)
    cnt[ int(ts.strftime("%j")) - 1 ] += 1
  else:
    running = 0
#  if running > 2:
#    ts -= mx.DateTime.RelativeDateTime(days=1)
#    cnt[ int(ts.strftime("%j")) - 1 ] += 1

for y in range(0,366):
  ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=y)
  print '%s,%s' % (ts.strftime("%Y-%m-%d"), cnt[y])
