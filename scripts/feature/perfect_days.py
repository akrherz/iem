
from pyIEM import iemdb 
i = iemdb.iemdb()
asos = i['asos']
coop = i['coop']

# Extract normals
ahighs = {}
rs = coop.query("SELECT high, valid from climate51 where station = 'ia2203'").dictresult()
for i in range(len(rs)):
  ahighs[ rs[i]['valid'] ] = rs[i]['high']

# Extract daily stats
rs = asos.query("""SELECT date(valid) as d, 
  sum( case when skyc1 in ('BKN','OVC') or skyc2 in ('BKN','OVC') or skyc3 in ('BKN','OVC') then 1 else 0 end ) as clouds, 
  max(tmpf) as high, max(dwpf) as maxd,
  max(sknt) as wind from alldata where 
  station = 'DSM' and tmpf > -50 and sknt >= 0 and valid > '1950-01-01' GROUP by d""").dictresult()
yrs = [0]*117
mos = [0]*12
for i in range(len(rs)):
  climate =  ahighs[ "2000-"+ rs[i]['d'][5:] ]
  month = int(rs[i]['d'][5:7])
  if rs[i]['clouds'] < 2 and rs[i]['wind'] < 17 and rs[i]['maxd'] < 60:
    if ((month in (12,1,2) and (rs[i]['high'] ) > climate) or
        (month in (3,4,5,9,10,11) and (rs[i]['high'] ) > climate) or
        (month in (6,7,8) and (rs[i]['high'] ) < climate)):
      y = int(rs[i]['d'][:4])
      if y == 2010:
        print rs[i]
      yrs[ y - 1950 ] += 1
      mos[month-1] += 1

for y in range(1950,2011):
  print '%s,%s' % (y, yrs[y-1950])
for y in range(0,12):
  print '%s,%s' % (y, mos[y])
