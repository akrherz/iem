import iemdb
import math
import network
nt = network.Table(('IA_ASOS','MO_ASOS','IL_ASOS', 'ND_ASOS', 'AWOS',
          'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS',
          'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS'))
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

def wchtidx(tmpf, sped):
  if (sped < 3):
    return tmpf
  wci = math.pow(sped,0.16);

  return 35.74 + .6215 * tmpf - 35.75 * wci + \
     + .4275 * tmpf * wci

for station in nt.sts.keys():
    #if nt.sts[station]['archive_begin'] is None:
    #    continue
    #if nt.sts[station]['archive_begin'].year > 1974:
    #    continue
    acursor.execute("""SELECT to_char(valid, 'YYYYMMDDHH24') as h, 
      tmpf, sknt from alldata where station = %s and tmpf < 40 and
      sknt >= 0 and tmpf > -60
      and valid BETWEEN '1973-01-01' and '2013-01-01' ORDER by h ASC""", (station,))
    lastval = "0000"
    cnt = 0
    minv = 0
    years = []
    for row in acursor:
        if row[0][:4] not in years:
            years.append( row[0][:4] )
        f = wchtidx(row[1], row[2]*1.15) #mph
        if f <= 0 and lastval != row[0]:
            cnt += 1
            if f < minv:
                minv = f
        lastval = row[0]

    print '%s,%s,%s,%.1f' % (station, cnt, len(years), minv)
