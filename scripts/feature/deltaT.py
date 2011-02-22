import network

nt = network.Table('IACLIMATE')
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

maxUp = [0]*14
maxUpStation = [0]*14
maxUpDate = [0]*14
maxDown = [0]*14
maxDownStation = [0]*14
maxDownDate = [0]*14

for id in nt.sts.keys():
  ccursor.execute("""
  SELECT day, high, low from alldata where stationid = %s ORDER by day ASC
  """, (id.lower(),))
  highs = [None]*14
  lows = [None]*14
  for row in ccursor:
    highs.pop()
    highs.insert(0,row[1])
    lows.pop()
    lows.insert(0,row[2])
    if highs[-1] is None:
      continue
    for dy in range(0,14):
      if (lows[0] - highs[dy]) < maxDown[dy]:
        maxDown[dy] = lows[0] - highs[dy]
        maxDownStation[dy] = id
        maxDownDate[dy] = row[0]
      if (highs[dy] - lows[13]) > maxUp[13-dy]:
        maxUp[13-dy] = highs[dy] - lows[13]
        maxUpStation[13-dy] = id
        maxUpDate[13-dy] = row[0]

print 'Maximum Rise End Date'
for i in range(14):
  print '%02i %s %s %3i' % (i, maxUpStation[i], maxUpDate[i], maxUp[i])
print 'Maximum Fall End Date'
for i in range(14):
  print '%02i %s %s %3i' % (i, maxDownStation[i], maxDownDate[i], maxDown[i])
