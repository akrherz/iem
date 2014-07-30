#!/mesonet/python-2.4/bin/python

import re, numarray
from numarray.libnumeric import histogram

lines = open('areas.txt').readlines()

t1 = []
t2 = []
t3 = []

for line in lines:
  tokens = re.split("\t", line)
  if (tokens[0] != ''):
    t1.append( float(tokens[0]) )
  if (tokens[1] != ''):
    t2.append( float(tokens[1]) )
  t3.append( float(tokens[2][:-1]) )

t1 = numarray.array( t1 )
t2 = numarray.array( t2 )
t3 = numarray.array( t3 )

print t1 / 1000000
