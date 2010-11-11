# Generate some comparison data between ASOS sites, tricky, me thinks

import iemdb
import datetime
import numpy
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

station1 = 'DSM'
station2 = 'ALO'

def get_data(year, station):
    data = {}
    acursor.execute("""SELECT valid, tmpf from t"""+year+""" where station = %s
    
    and (extract(minute from valid) between 50 and 59 or 
        extract(minute from valid) = 0)
    and tmpf is not null and tmpf > -50 and tmpf < 120""", (station,
                                    ))
    for row in acursor:
        valid = row[0] + datetime.timedelta(minutes=10)
        lkp = valid.strftime('%Y%m%d%H')
        data[lkp] = row[1]
        
    return data

years = 2011-1973
#diffs = numpy.zeros((years,24), 'f')
#cnts = numpy.zeros((years,24), 'f')
diffs = numpy.zeros((366,24), 'f')
cnts = numpy.zeros((366,24), 'f')


for year in range(1973,2011):
    data1 = get_data(str(year), station1)
    data2 = get_data(str(year), station2)

    for key in data1.keys():
        if data2.has_key(key):
            hr = int(key[-2:])
            dy = int(mx.DateTime.strptime(key, '%Y%m%d%H').strftime("%j"))
            diffs[year-1973,hr] += (data1[key] - data2[key])
            cnts[year-1973,hr] += 1.0
            diffs[dy-1,hr] += (data1[key] - data2[key])
            cnts[dy-1,hr] += 1.0

import matplotlib.pyplot as plt

data = diffs / cnts
print data

fig = plt.figure()
ax = fig.add_subplot(111)

res = ax.imshow( data, aspect='auto', rasterized=True, interpolation=None,
                 vmax=7, vmin=-7)
fig.colorbar(res)


ax.set_xlim(-0.5,23.5)
ax.set_xticks((0,4,8,12,16,20))
ax.set_xticklabels( ('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))

#ax.set_ylim(-0.5,365.5)
#ax.set_yticks((2,7,12,17,22,27,32,37))
#ax.set_yticklabels(('1975','1980','1985', '1990', '1995', '2000', '2005', '2010'))
ax.set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )

ax.grid(True)

ax.set_title("Des Moines - Waterloo Temperature Difference $^{\circ}\mathrm{F}$")

import iemplot
fig.savefig('test.png')
#iemplot.makefeature('test')

