import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from mpl_toolkits.basemap import Basemap

(fig, ax) = plt.subplots(2,1)

m = Basemap(projection='cea',llcrnrlat=40,urcrnrlat=44,
            llcrnrlon=-101,urcrnrlon=-87,resolution='i',
            ax=ax[0], fix_aspect=False)
m2 = Basemap(projection='cea',llcrnrlat=40,urcrnrlat=44,
            llcrnrlon=-101,urcrnrlon=-87,resolution='i',
            ax=ax[1], fix_aspect=False)

x,y= m(-107,40)
x2,y2=m(-87,50)

img=mpimg.imread('/tmp/FEMA_NorthernPlains.2012267.aqua.1km.jpg')
ax[0].imshow(img, extent=(x,x2,y, y2) )
ax[0].set_title("23 September 2012 :: Aqua MODIS True Color")

img=mpimg.imread('/tmp/FEMA_NorthernPlains.2013266.aqua.1km.jpg')
ax[1].imshow(img, extent=(x,x2,y, y2) )
ax[1].set_title("23 September 2013 :: Aqua MODIS True Color")

m.drawstates(linewidth=2.5)
m2.drawstates(linewidth=2.5)

plt.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
