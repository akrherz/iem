# Generate a report of duration of certain temperature thresholds

_REPORTID = "27"

def wrap(cnt, s=None):
  if cnt > 0:
    return s or cnt
  else:
    return ""

def write(mydb, rs, stationID):
  import constants, mx.DateTime
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# First occurance of record consecuative number of days 
# above or below a temperature threshold
""")
  out.write("#   %-27s %-27s  %-27s %-27s\n" % (" Low Cooler Than", 
     " Low Warmer Than", " High Cooler Than", " High Warmer Than") )
  out.write("%3s %5s %10s %10s %5s %10s %10s  %5s %10s %10s %5s %10s %10s\n" % (
      'TMP', 'DAYS', 'BEGIN DATE', 'END DATE',
      'DAYS', 'BEGIN DATE', 'END DATE',
      'DAYS', 'BEGIN DATE', 'END DATE',
      'DAYS', 'BEGIN DATE', 'END DATE') )

  data = {}
  for thres in range(-20,100,2):
    max_ah = 0
    max_bh = 0
    max_al = 0
    max_bl = 0
    cnt_ah = 0
    cnt_bh = 0
    cnt_al = 0
    cnt_bl = 0
    max_ah_ts = constants._QCENDTS
    max_bh_ts = constants._QCENDTS
    max_al_ts = constants._QCENDTS
    max_bl_ts = constants._QCENDTS
    for i in range(len(rs)):
      # High Above Threshold
      if rs[i]['high'] > thres :
        cnt_ah += 1
      if rs[i]['high'] <= thres and cnt_ah > 0:
        if cnt_ah > max_ah:
          ts = mx.DateTime.strptime(rs[i]['day'], '%Y-%m-%d')
          max_ah = cnt_ah
          max_ah_ts = ts
        cnt_ah = 0
      # Low Above Threshold
      if rs[i]['low'] > thres :
        cnt_al += 1
      if rs[i]['low'] <= thres and cnt_al > 0:
        if cnt_al > max_al:
          ts = mx.DateTime.strptime(rs[i]['day'], '%Y-%m-%d')
          max_al = cnt_al
          max_al_ts = ts
        cnt_al = 0
      # High Below Threshold
      if rs[i]['high'] < thres :
        cnt_bh += 1
      if rs[i]['high'] >= thres and cnt_bh > 0:
        if cnt_bh > max_bh:
          ts = mx.DateTime.strptime(rs[i]['day'], '%Y-%m-%d')
          max_bh = cnt_bh
          max_bh_ts = ts
        cnt_bh = 0
      # Low Below Threshold
      if rs[i]['low'] < thres :
        cnt_bl += 1
      if rs[i]['low'] >= thres and cnt_bl > 0:
        if cnt_bl > max_bl:
          ts = mx.DateTime.strptime(rs[i]['day'], '%Y-%m-%d')
          max_bl = cnt_bl
          max_bl_ts = ts
        cnt_bl = 0

    if cnt_ah > max_ah:
      ts = mx.DateTime.strptime(rs[i]['day'], '%Y-%m-%d')
      max_ah = cnt_ah
      max_ah_ts = ts
    if cnt_bh > max_bh:
      ts = mx.DateTime.strptime(rs[i]['day'], '%Y-%m-%d')
      max_bh = cnt_bh
      max_bh_ts = ts
    if cnt_al > max_al:
      ts = mx.DateTime.strptime(rs[i]['day'], '%Y-%m-%d')
      max_al = cnt_al
      max_al_ts = ts
    if cnt_bh > max_bh:
      ts = mx.DateTime.strptime(rs[i]['day'], '%Y-%m-%d')
      max_bh = cnt_bh
      max_bh_ts = ts

    out.write("%3i %5s %10s %10s %5s %10s %10s  %5s %10s %10s %5s %10s %10s\n" % (
    thres, 
    wrap(max_bl), 
    wrap(max_bl, (max_bl_ts - mx.DateTime.RelativeDateTime(days=max_bl)).strftime("%m/%d/%Y")), 
    wrap(max_bl, max_bl_ts.strftime("%m/%d/%Y") ),

    wrap(max_al), 
    wrap(max_al, (max_al_ts - mx.DateTime.RelativeDateTime(days=max_al)).strftime("%m/%d/%Y")), 
    wrap(max_al, max_al_ts.strftime("%m/%d/%Y") ),

    wrap(max_bh), 
    wrap(max_bh, (max_bh_ts - mx.DateTime.RelativeDateTime(days=max_bh)).strftime("%m/%d/%Y")), 
    wrap(max_bh, max_bh_ts.strftime("%m/%d/%Y") ),

    wrap(max_ah), 
    wrap(max_ah, (max_ah_ts - mx.DateTime.RelativeDateTime(days=max_ah)).strftime("%m/%d/%Y")), 
    wrap(max_ah, max_ah_ts.strftime("%m/%d/%Y") )
  ) )

  out.close()
