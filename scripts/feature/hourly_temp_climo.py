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
    acursor.execute("""SELECT valid, tmpf from t"""+year+""" where station = %s
    
    and (extract(minute from valid) between 50 and 59 or 
        extract(minute from valid) = 0)
    and tmpf is not null and tmpf > -50 and tmpf < 120""", (station,
                                    ))
    for row in acursor:
        valid = row[0] + datetime.timedelta(minutes=10, hours=-5)
        lkp = valid.strftime('%Y%m%d%H')
        data[lkp] = row[1]
        
    return data

years = 2011-1973
#totals = numpy.zeros((years,24), 'f')
#cnts = numpy.zeros((years,24), 'f')
totals = numpy.zeros((366,24), 'f')
cnts = numpy.zeros((366,24), 'f')

station1 = 'DSM'
for year in range(1950,2011):
    data1 = get_data(str(year), station1)
    
    for key in data1.keys():      
        hr = int(key[-2:])
        ts = mx.DateTime.strptime(key, '%Y%m%d%H')
        dy = int(ts.strftime("%j"))
        totals[dy-1,hr] += data1[key] 
        cnts[dy-1,hr] += 1.0
  
            
import matplotlib.pyplot as plt

data = totals / cnts
print totals[333,:]
print cnts[333,:]
print data[333,:]
# daily average
avg = numpy.average(data,1)
print avg[333]
print numpy.shape(avg)
for dy in range( numpy.shape(data)[0]):
    data[dy,:] = data[dy,:] - avg[dy]
    #print dy, avg[dy], data[dy,-1]
v = max( numpy.max(data), 0 - numpy.min(data) )
#print v


fig = plt.figure()
ax = fig.add_subplot(111)

res = ax.imshow( data[:-1,:], aspect='auto', rasterized=True, interpolation=None,
                 vmax=v, vmin=(0-v))
fig.colorbar(res)


ax.set_xlim(-0.5,23.5)
ax.set_xticks((0,4,8,12,16,20))
ax.set_xticklabels( ('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))
ax.set_xlabel("All times CDT")

#ax.set_ylim(-0.5,365.5)
#ax.set_yticks((2,7,12,17,22,27,32,37))
#ax.set_yticklabels(('1975','1980','1985', '1990', '1995', '2000', '2005', '2010'))
ax.set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )

ax.grid(True)

ax.set_title("Des Moines Hourly Temperature Departure\nVersus Daily Average (1950-2010) $^{\circ}\mathrm{F}$")

import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
