
import pg
import mx.DateTime
#"""

conn = pg.connect("coop", "iemdb", user="nobody")

rs = conn.query("SELECT day, high, low, precip from alldata where station = 'IA2203' ORDER by day ASC").dictresult()

def check_hot(ar, ts):
    if len(ar) > 10:
        print 'HOT,%s,%s,%s' % (len(ar), ar[0], ts)
def check_cold(ar, ts):
    if len(ar) > 10:
        print 'COLD,%s,%s,%s' % (len(ar), ar[0], ts)

records = {}
hot_running = []
cold_running = []
for row in rs:
    ts = mx.DateTime.strptime(row['day'], '%Y-%m-%d')
    lookup = ts.strftime("%m%d")
    if not records.has_key(lookup):
        records[lookup] = {'max_high': -1000, 'min_high': 1000, 
                           'max_low': -1000, 'min_low': 1000}
    if row['high'] <= records[ lookup ]['min_high']:
        records[ lookup ]['min_high'] = row['high']
        cold_running.append( ts )
        check_hot( hot_running, ts )
        hot_running = []
    if row['low'] <= records[ lookup ]['min_low']:
        records[ lookup ]['min_low'] = row['low']
        cold_running.append( ts )
        check_hot( hot_running, ts )
        hot_running = []
    if row['high'] >= records[ lookup ]['max_high']:
        print ts, row['high']
        records[ lookup ]['max_high'] = row['high']
        hot_running.append( ts )
        check_cold( cold_running , ts)
        cold_running = []
    if row['low'] >= records[ lookup ]['max_low']:
        records[ lookup ]['max_low'] = row['low']
        hot_running.append( ts )
        check_cold( cold_running , ts)
        cold_running = []
#"""

H = """HOT,55,2010-05-23 00:00:00.00,2013-05-02 00:00:00.00
HOT,45,1934-05-06 00:00:00.00,1934-08-25 00:00:00.00
HOT,39,1936-05-06 00:00:00.00,1936-10-01 00:00:00.00
HOT,36,1913-06-15 00:00:00.00,1913-09-20 00:00:00.00
HOT,33,1901-06-15 00:00:00.00,1901-08-03 00:00:00.00"""

labels = []
ys = range(10,0,-1)
xs = []
for line in H.split("\n"):
    tokens = line.split(",")
    xs.append( float(tokens[1]) )
    ts1 = mx.DateTime.strptime(tokens[2][:10], '%Y-%m-%d')
    ts2 = mx.DateTime.strptime(tokens[3][:10], '%Y-%m-%d')
    fmt1 = "%-d %b %Y"
    if ts1.year == ts2.year:
        fmt1 = "%-d %b"
    labels.append("%s - %s" % ( ts1.strftime(fmt1) , 
                                ts2.strftime("%-d %b %Y")))

C = """COLD,23,1915-05-17 00:00:00.00,1915-10-27 00:00:00.00
COLD,23,1911-09-24 00:00:00.00,1912-04-25 00:00:00.00
COLD,23,1907-04-10 00:00:00.00,1907-06-16 00:00:00.00
COLD,22,1936-01-23 00:00:00.00,1936-05-06 00:00:00.00
COLD,21,1902-06-19 00:00:00.00,1902-10-25 00:00:00.00"""

for line in C.split("\n"):
    tokens = line.split(",")
    xs.append( float(tokens[1]) )
    ts1 = mx.DateTime.strptime(tokens[2][:10], '%Y-%m-%d')
    ts2 = mx.DateTime.strptime(tokens[3][:10], '%Y-%m-%d')
    fmt1 = "%-d %b %Y"
    if ts1.year == ts2.year:
        fmt1 = "%-d %b"
    labels.append("%s - %s" % ( ts1.strftime(fmt1) , 
                                ts2.strftime("%-d %b %Y")))

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1, frameon=False)

ax.barh(ys[:5], xs[:5], fc='r', alpha=0.5)
ax.barh(ys[5:], xs[5:], fc='b', alpha=0.5)
for x,y,l in zip(xs, ys, labels):
    ax.text(0, y + 0.2, l)
    ax.text(x+0.5, y+0.5, "%.0f" % (x,), va='center')
    
ax.text(-0.5,8.4, "Largest 5 Hot Streaks", rotation=90, bbox=dict(fc='r', ec='None', alpha=0.2),
        va='center', ha='right')
ax.text(-0.5,3.4, "Largest 5 Cold Streaks", rotation=90, bbox=dict(fc='b', ec='None', alpha=0.2),
        va='center', ha='right')
ax.set_xlim(left=-3)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
ax.set_ylim(0.3, 11.0)
ax.set_xlabel("Consecutive Events")
ax.set_title("Des Moines Largest Streaks of Record Events after 1900\nPeriod with only warm or cold daily temperature records set")
fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')
