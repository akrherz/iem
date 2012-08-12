import matplotlib.pyplot as plt
import math
import numpy

reports0 = []
dirs0 = []
sped0 = []
reports1 = []
dirs1 = []
sped1 = []

reports2 = []
dirs2 = []
sped2 = []

for line in open('data').readlines():
    r,d,s = line.split(",")
    if float(r) == 0:
        reports0.append( float(r) )
        dirs0.append( float(d) )
        sped0.append( float(s) )
    elif float(r) < 5:
        reports1.append( float(r) )
        dirs1.append( float(d) )
        sped1.append( float(s) )
    else:
        reports2.append( float(r) )
        dirs2.append( float(d) )
        sped2.append( float(s) )

reports0 = numpy.array(reports0)
dirs0 = numpy.array( dirs0 )
sped0 = numpy.array( sped0 )

reports1 = numpy.array(reports1)
dirs1 = numpy.array( dirs1 )
sped1 = numpy.array( sped1 )

reports2 = numpy.array(reports2)
dirs2 = numpy.array( dirs2 )
sped2 = numpy.array( sped2 )

import matplotlib.pyplot as plt

fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, polar=True)


theta_angles = numpy.arange(0, 360, 45)
theta_labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE']
ax.set_thetagrids(angles=theta_angles, labels=theta_labels)
#ax.set_rgrids(numpy.arange(0,30,5), angle=math.pi)

ax.set_title("SPC Tornado Watches in Iowa [1 Jan 2002 - 9 Jul 2011]\nWatch Box Mean Wind [kts] and Tornado Reports")
ax.scatter( - dirs0 + math.pi/2.,  sped0 / 0.514, marker='x', s=50, label='No Reports')
ax.scatter( - dirs1 + math.pi/2.,  sped1 / 0.514, marker='o', s=50, c='b', label='1-4')
ax.scatter( - dirs2 + math.pi/2.,  sped2 / 0.514, marker='o', s=50, c='r', label='5+')
l = ax.legend(loc=(0.1,0.6))


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')