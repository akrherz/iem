import iemdb
import numpy as np
import numpy.ma

COOP = iemdb.connect('postgis', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 select extract(day from issue) as d, extract(year from issue) as y,
 count(*) from warnings WHERE gtype = 'C' and 
 wfo in ('DMX','DVN','FSD','OAX','ARX') and substr(ugc, 1,3) = 'IAC' 
 and extract(month from issue) = 5 and phenomena in ('SV','TO') 
 and significance = 'W' GROUP by d, y
""")
data = numpy.ma.zeros( (2013-1986,31), 'f')
for row in ccursor:
    data[row[1]-1986,row[0]-1] = row[2]
data.mask = numpy.where(data == 0, True, False)
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1,1)

#res = ax.contourf( data, extend='max')
res = ax.imshow( data, aspect='auto', rasterized=True, interpolation='nearest')
fig.colorbar(res)
ax.set_title("May Severe T'Storm + Tornado Warnings in Iowa\nCounty Based Warnings [1986-2012]")
ax.set_ylabel("Year")
ax.set_xlabel("Day of May")
ax.set_xticks([0,7,14,21,28])
ax.set_xticklabels([1,8,15,22,29])
ax.set_yticks([0,4,9,14,19,24])
ax.set_yticklabels([1986,1990,1995,2000,2005,2010])
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test') 
