import iemdb
import mx.DateTime
ASOS = iemdb.connect('asos')
acursor = ASOS.cursor()

obs = {}
for yr in range(2010,2013):
  acursor.execute("""SELECT valid at time zone 'UTC', precip from  t%s_1minute
  where station = 'DSM' and precip > 0""" % (yr,))
  for row in acursor:
    obs[ row[0].strftime("%Y%m%d%H%M") ] = row[1]

output = open('desmoines2.txt', 'w')
lastts = mx.DateTime.DateTime(2010,10,25, 0, 1)
lastdb = 0
for line in open('desmoines.txt').xreadlines():
  tokens = line.split(",")
  ts = mx.DateTime.strptime(tokens[0][:16], '%Y-%m-%d %H:%M')
  totalprecip = 0
  now = lastts
  while now < ts:
    totalprecip += obs.get( now.strftime("%Y%m%d%H%M"), 0)
    now += mx.DateTime.RelativeDateTime(minutes=1)
  if totalprecip > 0.04:
    print lastts, now, totalprecip, lastdb
  output.write("%s,%s,%s\n" % (lastts.strftime('%Y-%m-%d %H:%M'), lastdb, totalprecip))
  lastdb = tokens[1].strip()
  lastts = ts

output.close()

