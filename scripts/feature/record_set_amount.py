
import pg
import mx.DateTime

conn = pg.connect("coop", "iemdb", user="nobody")

rs = conn.query("SELECT day, high, low, precip from alldata where station = 'IA2203' and sday != '0229' ORDER by day ASC").dictresult()

min_high = {}

for row in rs:
  ts = mx.DateTime.strptime(row['day'], '%Y-%m-%d')
  lookup = ts.strftime("%m%d")
  if not min_high.has_key(lookup):
    min_high[lookup] = 1000
  if row['high'] < min_high[ lookup ]:
    diff = min_high[ lookup ] - row['high']
    if diff > 5:
        print 'NEW: %s OLD: %s DAY: %s' % (row['high'], min_high[lookup],
           ts)
    min_high[lookup] = row['high']

