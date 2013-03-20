"""
Gateway for B548 temps to nagios, this way I can setup alerts via it

Array("In Air Handler", "Out Air Handler", "Out Rack", "In Rack")
0 70.25
1 57.88
2 88.25
3 62.04
"""
import sys

data = open('/tmp/onewire.txt', 'r').readlines()
if len(data) != 4:
    print 'WARNING - Could not read file!'
    sys.exit(1)

v = []
for line in data:
    tokens = line.strip().split()
    if len(tokens) == 2:
        v.append( float(tokens[1]) )
    else:
        v.append( -99 )

ds = ""
ks = ["in_handler", "out_handler", "out_rack", "in_rack"]
for k,d in zip(ks, v):
    ds += "%s=%s;95;100;105 " % (k, d)

if v[2] < 95:
    print 'OK - room %s |%s' % (v[0], ds)
    sys.exit(0)
elif v[2] < 100:
    print 'WARNING - room %s |%s' % (v[0], ds)
    sys.exit(1)
else:
    print 'CRITICAL - room %s |%s' % (v[0], ds)
    sys.exit(2)