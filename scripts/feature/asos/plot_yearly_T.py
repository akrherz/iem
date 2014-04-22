import netCDF3
from matplotlib import pyplot as plt
import numpy
from scipy import stats
import pg
asos = pg.connect('asos', 'iemdb', user='nobody')

def k2f(ar):
  return (ar - 273.5 ) * 9.0/5.0 + 32.0

data = {}
for id in ('STL', 'DSM', 'MCI'):
    rs = asos.query("""SELECT extract(year from valid) as year, 
  avg(dwpf) from alldata WHERE station = '%s' 
  and dwpf > -50 and valid > '1973-01-01' 
  and valid < '2010-12-01' and 
  extract(month from valid) in (6,7,8) 
  GROUP by year ORDER by year ASC""" % (id,)).dictresult()

    d = []
    for i in range(len(rs)):
        d.append( rs[i]['avg'] )
    data[id] = d


fig = plt.figure(1, figsize=(10,8))
ax = fig.add_subplot(111)
width = 1.


ax.set_xticklabels( range(1973,2010,5) )
ax.set_xlim(0,len(d))
ax.set_ylabel(r"Dew Point [$^{\circ}\mathrm{F}$]")
ax.set_xlabel("Year")
ax.set_title("Mean June,July,August Dew Point\nDes Moines (DSM), Kansas City (MCI), Saint Louis (STL) (1973-2010)")

colors = {'DSM': 'g', 'MCI': 'b', 'STL': 'r'}

for id in ['DSM','STL', 'MCI']:
    h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(numpy.arange(len(d)),data[id])
    ax.plot([0,len(d)], [intercept, (len(d) * h_slope) + intercept], '%s--' % (colors[id],))
    ax.plot( range(len(d)), data[id], '%s' %( colors[id],),
         label=r"%s $\frac{\Delta T_d}{year} = %.3f,R^2=%.2f$" % (
                id, h_slope, h_r_value ** 2))
    print id, h_r_value, p_value

ax.legend(ncol=2, loc=4)
ax.set_ylim( 55, 70 )
ax.grid(True)
fig.savefig("test.png")

