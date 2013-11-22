import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pyiem.plot import MapPlot
import sys

year = int(sys.argv[1])
year2 = int(sys.argv[2])

x = []
y = []
x2 = []
y2 = []
for linenum, line in enumerate(open('visit_history_093013_st12.csv')):
    if linenum == 0:
        continue
    tokens = line.split(",")
    if int(tokens[5]) not in [year, year2]:
        continue
    try:
        if int(tokens[5]) == year:
            y.append( float(tokens[17].strip()) )
            x.append( float(tokens[18].strip()) )
        elif int(tokens[5]) == year2:
            y2.append( float(tokens[17].strip()) )
            x2.append( float(tokens[18].strip()) )
    except:
        continue

H2, xedges, yedges = np.histogram2d(y, x, bins=(50, 100),range=[[25,50],[-130,-60]])
H22, xedges, yedges = np.histogram2d(y2, x2, bins=(50, 100),range=[[25,50],[-130,-60]])

m = MapPlot(sector='conus', title='Heat Map of Change in Visitors %s(n=%s) minus %s(n=%s)' % (
                                                    year, len(x), year2, len(x2)), 
            subtitle='from visit_history_093013_st12.csv',nologo=True)
x,y = np.meshgrid(yedges, xedges)

#levels = [1,2,5,7,10,15,20,25,30,40,50,60,70,80,90,100,200]
levels = np.arange(-60,61,5)
H3 = ma.array(H2 - H22)
H3.mask = np.where(H2 < 1, True, False)

cmap = cm.get_cmap('jet')
cmap.set_under('black')
cmap.set_over('black')
m.pcolormesh(x,y, H3, levels, cmap=cmap, units='count')
#m.drawcounties()
m.postprocess(filename='conus_heatmap_%s_%s.png' % (year, year2))
