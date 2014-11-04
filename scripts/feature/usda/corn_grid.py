import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import datetime
import numpy as np

(fig, ax) = plt.subplots(1,1)

df = pd.read_csv('corn.csv')

df.sort("Week Ending",ascending=True, inplace=True)

data = np.ma.ones((2015-1981, 366), 'f') * -1
data.mask = np.where(data == -1, True, False)

lastrow = None
for rownum, row in df.iterrows():
    if lastrow is None:
        lastrow = row
        continue
    
    date = datetime.datetime.strptime(row["Week Ending"], "%Y-%m-%d")
    ldate = datetime.datetime.strptime(lastrow["Week Ending"], "%Y-%m-%d")
    val = int(row['Value'])
    lval = int(lastrow['Value'])
    d0 = int(ldate.strftime("%j"))
    d1 = int(date.strftime("%j"))
    if ldate.year == date.year:
        delta = (val - lval) / float(d1-d0)
        for i, jday in enumerate(range(d0, d1+1)):
            data[date.year-1981, jday] = lval + i * delta
    else:
        data[ldate.year-1981, d0:] = 100
    
    lastrow = row
    
d2014 = np.max(data[-1,:])
for year in range(1981, 2014):
    idx = np.digitize([d2014,], data[year-1981, :])
    ax.text(idx[0], year, "X", va='center', zorder=2)
    
cmap = cm.get_cmap('jet')
res = ax.imshow(data, extent=[1,367,2014.5,1980.5], aspect='auto',
                interpolation='none', cmap=cmap)
fig.colorbar(res)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(200,360)
ax.set_ylim(2014.5, 1980.5)
ax.grid(True)
ax.set_xlabel("X denotes 2 Nov 2014 value of %.0f%%" % (d2014,))
ax.set_title("USDA NASS 1981-2014 Iowa Corn Harvest Progress\nDaily Linear Interpolated Values Between Weekly Reports")
fig.savefig('test.png')