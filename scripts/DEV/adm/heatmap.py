import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pyiem.plot import MapPlot
import sys

year = int(sys.argv[1])

x = []
y = []
for linenum, line in enumerate(open('visit_history_093013_st12.csv')):
    if linenum == 0:
        continue
    tokens = line.split(",")
    if int(tokens[5]) != year:
        continue
    try:
        y.append( float(tokens[17].strip()) )
        x.append( float(tokens[18].strip()) )
    except:
        continue

H2, xedges, yedges = np.histogram2d(y, x, bins=(50, 100),range=[[25,50],[-130,-60]])

m = MapPlot(sector='conus', title='Heat Map of Location of Visitors, year=%s' % (year,), 
            subtitle='from visit_history_093013_st12.csv',nologo=True)
x,y = np.meshgrid(yedges, xedges)

levels = [1,2,5,7,10,15,20,25,30,40,50,60,70,80,90,100,200]
H3 = ma.array(H2)
H3.mask = np.where(H2 < 1, True, False)

cmap = cm.get_cmap('jet')
cmap.set_under('white')
cmap.set_over('black')
m.pcolormesh(x,y, H3, levels, cmap=cmap, units='count')
#m.drawcounties()
m.postprocess(filename='conus_heatmap_%s.png' % (year,))
