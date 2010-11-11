import netCDF3
from matplotlib import pyplot as plt
import numpy
from scipy import stats
import pg

asos = pg.connect('asos', 'iemdb', user='nobody')

def k2f(ar):
  return (ar - 273.5 ) * 9.0/5.0 + 32.0

rs = asos.query("SELECT dwpf, valid from alldata WHERe station = 'MCI' and dwpf > -50 and valid > '1973-01-01'").dictresult()

data = []
data2 = []
for i in range(len(rs)):
  if int(rs[i]['valid'][:4]) > 1986:
    data2.append( rs[i]['dwpf'] )
  else:
    data.append( rs[i]['dwpf'] )

fig = plt.figure()
ax = fig.add_subplot(111)
width = 0.35

n, bins, patches = ax.hist(data, 25, normed=1, histtype='step', label='Prior 1986')
n, bins, patches = ax.hist(data2, bins=bins, normed=1, histtype='step', label='1986 and after')

ax.legend()

#ax.set_xticklabels( range(1970,2010,5) )
ax.set_xlabel("Dew Point [F]")
ax.set_ylabel("Frequency")
ax.set_title("Dew Point Distribution Saint Louis (KSTL) (1973-2010)")


#ax.set_ylim( 40, 90 )
ax.grid( True )

fig.savefig("test.png")

