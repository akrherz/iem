import iemdb
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute("""
  SELECT valid, vsby from alldata where station = 'RST' 
  and valid > '1933-06-01' ORDER by valid ASC
""")
running = False
last = None
lmax = 0
lcnt = 0
for row in acursor:
    ts = mx.DateTime.strptime(row[0].strftime("%Y%m%d%H%M"), "%Y%m%d%H%M")
    if running and row[1] <= 0.2:
        lcnt += 1
        continue
    if not running and row[1] < 0.2:
        last = ts
        running = True
        continue
    if running and row[1] > 0.2:
        diff = (ts - last).hours
        if diff > lmax and (diff - lcnt) < 5:
            print 'New', diff, row[0], lcnt
            lmax = diff
        lcnt = 0
        running = False

