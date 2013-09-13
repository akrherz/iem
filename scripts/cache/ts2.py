'''
Fuzzy math to get the right timestamp

if 15, we want 00
if 45, we want 30
'''
import datetime
import sys

gmt = datetime.datetime.utcnow()

cycle = int(sys.argv[1])

if cycle == 15:
    gmt = gmt.replace(minute=0)
else:
    gmt -= datetime.timedelta(hours=1)
    gmt = gmt.replace(minute=30)

print gmt.strftime( sys.argv[2] )
