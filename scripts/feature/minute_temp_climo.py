# Generate some comparison data between ASOS sites, tricky, me thinks

import iemdb
import datetime
import numpy
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
acursor.execute("SET TIME ZONE 'GMT'")

def get_data(year, station):
    data = {}
    acursor.execute("""SELECT valid, tmpf from t"""+year+"""_1minute 
    where station = %s
    and tmpf is not null and tmpf >= -40 and tmpf < 120""", (station,
                                    ))
    for row in acursor:
        valid = row[0] - datetime.timedelta(hours=5)
        lkp = valid.strftime('%Y%m%d%H%M')
        data[lkp] = row[1]
        
    return data

years = 2011-1973
#totals = numpy.zeros((years,24), 'f')
#cnts = numpy.zeros((years,24), 'f')
totals = numpy.zeros((366,1440), 'f')
cnts = numpy.zeros((366,1440), 'f')



station1 = 'DSM'
for year in range(2000,2011):
    data1 = get_data(str(year), station1)
    
    for key in data1.keys():      
        hr = int(key[-4:-2])
        mi = int(key[-2:])
        offset = hr * 60 + mi
        dy = int(mx.DateTime.strptime(key, '%Y%m%d%H%M').strftime("%j"))
        totals[dy-1,offset] += data1[key] 
        cnts[dy-1,offset] += 1.0
        
import matplotlib.pyplot as plt

data = totals / cnts
avg = numpy.average(data,1)

for dy in range( numpy.shape(data)[0]):
    data[dy,:] = data[dy,:] - avg[dy]
    #print dy, avg[dy], data[dy,-1]
#v = max( numpy.max(data), 0 - numpy.min(data) )

import netCDF3
nc = netCDF3.Dataset('tmp2.nc', 'w')
nc.createDimension('day', 365)
nc.createDimension('minute', 1440)
v = nc.createVariable('data', numpy.float, ('day', 'minute'))

v[:,:] = data[:365,:]
# Now we average over the month!
#for i in range(12):
#    v[i,:] = numpy.average( data[i*30:(i*30)+30,:],0)
    

nc.close()

fig = plt.figure()
ax = fig.add_subplot(111)

res = ax.imshow( data, aspect='auto', rasterized=True, interpolation=None,
                 vmin=-12.,vmax=12.)
fig.colorbar(res)


ax.set_xlim(-0.5,1439.5)
ax.set_xticks((0,4*60,8*60,12*60,16*60,20*60))
ax.set_xticklabels( ('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))
ax.set_xlabel('All times CDT')

#ax.set_ylim(-0.5,365.5)
#ax.set_yticks((2,7,12,17,22,27,32,37))
#ax.set_yticklabels(('1975','1980','1985', '1990', '1995', '2000', '2005', '2010'))
ax.set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )

ax.grid(True)

ax.set_title("Des Moines Temperature Diurnal Cycle\nAgainst Daily Average (2000-2010) $^{\circ}\mathrm{F}$")

import iemplot
fig.savefig('test.png')
#iemplot.makefeature('test')
