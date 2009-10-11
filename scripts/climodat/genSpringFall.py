"""
Generate the length of a growing season given some base threshold
"""


def write(mydb, rs, stationID, base, _REPORTID):
  import constants, mx.DateTime
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# LENGTH OF SEASON FOR STATION NUMBER  %s   BASE TEMP=%s
# LAST SPRING OCCURENCE FIRST FALL OCCURENCE 
   YEAR MONTH DAY DOY         MONTH DAY DOY   LENGTH OF SEASON\n""" \
   % (stationID, base) )

  s = mx.DateTime.DateTime(constants.startyear(stationID), 1, 1)
  e = constants._ENDTS
  interval = mx.DateTime.RelativeDateTime(years=+1)

  now = s
  d = {}
  while now <= e:
    ep = now + mx.DateTime.RelativeDateTime(month=12, day=1)
    sp = now + mx.DateTime.RelativeDateTime(month=1, day=1)
    d[int(now.year)] = {'sts': sp, 'ets': ep}
    now += interval

  for i in range(len(rs)):
    low = int(rs[i]["low"])
    if low > base:
      continue
    ts = mx.DateTime.strptime(rs[i]["day"], "%Y-%m-%d")
    mp = ts + mx.DateTime.RelativeDateTime(month=7, day=1)
    if (ts > mp): # Fall
      if (ts < d[ int(ts.year) ]['ets'] ): 
        d[int(ts.year)]['ets'] = ts
    else:
      if (ts > d[ int(ts.year) ]['sts'] ): 
        d[int(ts.year)]['sts'] = ts

  sjdaytot = 0
  ejdaytot = 0
  yrs = 0
  for yr in range(constants.startyear(stationID), constants._ENDYEAR):
    if (yr == constants._THISYEAR):
      continue
    yrs += 1
    sjdaytot += int(d[yr]['sts'].strftime("%j"))
    ejdaytot += int(d[yr]['ets'].strftime("%j"))
    out.write("%7i%4i%6i%4i        %4i%6i%4i          %3s\n" \
      % (yr, d[yr]['sts'].month, d[yr]['sts'].day, \
         int(d[yr]['sts'].strftime("%j")),\
         d[yr]['ets'].month, d[yr]['ets'].day, \
         int(d[yr]['ets'].strftime("%j") ), \
         (d[yr]['ets'] - d[yr]['sts']).strftime("%d") ) )

  smean = sjdaytot / yrs
  emean = ejdaytot / yrs
  sts = mx.DateTime.DateTime(2001,1,1) + mx.DateTime.RelativeDateTime(days=smean)
  ets = mx.DateTime.DateTime(2001,1,1) + mx.DateTime.RelativeDateTime(days=emean)

  out.write("%7s%4i%6i%4i        %4i%6i%4i          %3s\n" \
    % ("MEAN", sts.month, sts.day, smean, ets.month, ets.day, 
       emean, emean - smean) )
  out.close()
