import netCDF3
from matplotlib import pyplot as plt
import numpy
from scipy import stats
import pg
asos = pg.connect('asos', 'iemdb', user='nobody')

def k2f(ar):
  return (ar - 273.5 ) * 9.0/5.0 + 32.0

rs = asos.query("SELECT extract(year from valid) as year, avg(dwpf) from alldata WHERE station = 'STL' and dwpf > -50 and valid > '1973-01-01' and valid < '2010-01-01' and extract(month from valid) in (12,1,2) GROUP by year ORDER by year ASC").dictresult()

data = []
for i in range(len(rs)):
  data.append( rs[i]['avg'] )



fig = plt.figure()
ax = fig.add_subplot(111)
width = 1.
bar1 = ax.bar( numpy.arange(len(data)), data, width, color='r' )

ax.set_xticklabels( range(1973,2010,5) )
ax.set_ylabel("Dew Point [F]")
ax.set_xlabel("Year")
ax.set_title("Mean DJF Dew Point for Saint Louis (KSTL) (1973-2009)")

h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(numpy.arange(len(data)),data)
ax.plot([0,len(data)], [intercept, (len(data) * h_slope) + intercept], color='r')
print h_r_value, p_value

ax.legend( (bar1[0],), (r"$\frac{dT_d}{dyear} = %.3f , R^2 = %.2f$" % (h_slope, h_r_value ** 2), ) )

ax.set_ylim( 0, 40 )

fig.savefig("test.png")

