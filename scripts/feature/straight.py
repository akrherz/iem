import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']
cnt = [0]*367
tot = [0]*367

rs = coop.query("""SELECT day, extract(doy from day) as doy, 
     CASE WHEN precip >= 0.01 THEN precip ELSE 0 END as rain 
     from alldata WHERE stationid = 'ia0200' ORDER by day ASC""").dictresult()

for i in range(6,len(rs)-6):
  if max( rs[i-3]['rain'], rs[i-2]['rain'], rs[i-1]['rain'], rs[i]['rain'],
          rs[i+1]['rain'], rs[i+2]['rain'], rs[i+3]['rain']) == 0:
    cnt[ int(rs[i]['doy']) ] += 1
  elif max( rs[i-4]['rain'], rs[i-3]['rain'], rs[i-2]['rain'], rs[i-1]['rain'],
          rs[i]['rain'], rs[i+1]['rain'], rs[i+2]['rain']) == 0:
    cnt[ int(rs[i]['doy']) ] += 1
  elif max( rs[i-5]['rain'], rs[i-4]['rain'], rs[i-3]['rain'], rs[i-2]['rain'],
          rs[i-1]['rain'], rs[i]['rain'], rs[i+1]['rain']) == 0:
    cnt[ int(rs[i]['doy']) ] += 1
  elif max( rs[i-6]['rain'], rs[i-5]['rain'], rs[i-4]['rain'], rs[i-3]['rain'],
          rs[i-2]['rain'], rs[i-1]['rain'], rs[i]['rain']) == 0:
    cnt[ int(rs[i]['doy']) ] += 1
  elif max( rs[i-2]['rain'], rs[i-1]['rain'], rs[i]['rain'], rs[i+1]['rain'],
          rs[i+2]['rain'], rs[i+3]['rain'], rs[i+4]['rain']) == 0:
    cnt[ int(rs[i]['doy']) ] += 1
  elif max( rs[i-1]['rain'], rs[i]['rain'], rs[i+1]['rain'], rs[i+2]['rain'],
          rs[i+3]['rain'], rs[i+4]['rain'], rs[i+5]['rain']) == 0:
    cnt[ int(rs[i]['doy']) ] += 1
  elif max( rs[i]['rain'], rs[i+1]['rain'], rs[i+2]['rain'], rs[i+3]['rain'],
          rs[i+4]['rain'], rs[i+5]['rain'], rs[i+6]['rain']) == 0:
    cnt[ int(rs[i]['doy']) ] += 1
  tot[ int(rs[i]['doy']) ] += 1


for i in range(1,367):
  ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=i-1)
  print "%s,%.4f" % (ts.strftime("%Y-%m-%d"), float(cnt[i]) / float(tot[i]) * 100.0)
