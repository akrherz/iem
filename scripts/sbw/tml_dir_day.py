import matplotlib.pyplot as plt
import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

doy = []
dir = []
sknt = []
pcursor.execute("""SELECT tml_direction, extract(doy from issue), tml_sknt from sbw
 WHERE issue > '2007-10-01' and tml_sknt >= 0 and ('DMX','DVN','ARX',
  'OAX','FSD') and status = 'NEW' and phenomena = 'SV'""")
for row in pcursor:
  doy.append( row[1] )
  dir.append( row[0] )
  sknt.append( row[0] )

import numpy
sknt = numpy.array( sknt )

fig, ax = plt.subplots(1,1)

ax.scatter(doy, dir, s=30, facecolor='r', alpha=0.05, edgecolor='r')
ax.set_xlim(0,366)
ax.set_ylim(0,360)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_yticks((0,45,90,135,180,225,270,315,360))
ax.set_yticklabels(('North','NE','East','SE','South','SW', 'West','NW','North'))
ax.set_ylabel("Storm Motion Direction From")
ax.grid(True)
ax.set_title("Iowa Severe Thunderstorm Storm Motion Vector\nBased on warnings by NWS offices covering Iowa 1 Oct 2007 - 5 May 2012")
ax.set_xlabel("* Each Warning has a 5% alpha transparency")

fig.savefig('test.png')
