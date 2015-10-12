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
        v.append(float(tokens[1]))
    else:
        v.append(-99)

ds = ""
ks = ["in_handler", "out_handler", "out_rack", "in_rack"]
maxes = [80, 70, 100, 75]
msg = ""
for k, d, m in zip(ks, v, maxes):
    ds += "%s=%s;%s;%s;%s " % (k, d, m, m+5, m+10)
    msg += "%s %s," % (k, d)
if v[3] < 75:
    print 'OK - %s |%s' % (msg, ds)
    sys.exit(0)
elif v[3] < 80:
    print 'WARNING - %s |%s' % (msg, ds)
    sys.exit(1)
else:
    print 'CRITICAL - %s |%s' % (msg, ds)
    sys.exit(2)
