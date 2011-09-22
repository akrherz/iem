import mx.DateTime
import iemdb
from pyIEM import mesonet
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

FAIRS = [
[mx.DateTime.DateTime(1880,9,6),mx.DateTime.DateTime(1880,9,10)],
[mx.DateTime.DateTime(1881,9,5),mx.DateTime.DateTime(1881,9,9)],
[mx.DateTime.DateTime(1882,9,1),mx.DateTime.DateTime(1882,9,8)],
[mx.DateTime.DateTime(1883,8,31),mx.DateTime.DateTime(1883,9,7)],
[mx.DateTime.DateTime(1884,8,29),mx.DateTime.DateTime(1884,9,5)],
[mx.DateTime.DateTime(1885,9,4),mx.DateTime.DateTime(1885,9,11)],
[mx.DateTime.DateTime(1886,9,3),mx.DateTime.DateTime(1886,9,11)],
[mx.DateTime.DateTime(1887,9,2),mx.DateTime.DateTime(1887,9,9)],
[mx.DateTime.DateTime(1888,8,31),mx.DateTime.DateTime(1888,9,7)],
[mx.DateTime.DateTime(1889,8,30),mx.DateTime.DateTime(1889,9,6)],
[mx.DateTime.DateTime(1890,8,29),mx.DateTime.DateTime(1890,9,5)],
[mx.DateTime.DateTime(1891,8,28),mx.DateTime.DateTime(1891,9,4)],
[mx.DateTime.DateTime(1892,8,26),mx.DateTime.DateTime(1892,9,2)],
[mx.DateTime.DateTime(1893,9,1),mx.DateTime.DateTime(1893,9,8)],
[mx.DateTime.DateTime(1894,8,31),mx.DateTime.DateTime(1894,9,7)],
[mx.DateTime.DateTime(1895,9,6),mx.DateTime.DateTime(1895,9,13)],
[mx.DateTime.DateTime(1896,9,4),mx.DateTime.DateTime(1896,9,11)],
[mx.DateTime.DateTime(1897,9,11),mx.DateTime.DateTime(1897,9,18)],
[mx.DateTime.DateTime(1899,8,25),mx.DateTime.DateTime(1899,9,1)],
[mx.DateTime.DateTime(1900,8,24),mx.DateTime.DateTime(1900,8,31)],
[mx.DateTime.DateTime(1901,8,23),mx.DateTime.DateTime(1901,8,30)],
[mx.DateTime.DateTime(1902,8,22),mx.DateTime.DateTime(1902,8,29)],
[mx.DateTime.DateTime(1903,8,21),mx.DateTime.DateTime(1903,8,28)],
[mx.DateTime.DateTime(1904,8,19),mx.DateTime.DateTime(1904,8,26)],
[mx.DateTime.DateTime(1905,8,25),mx.DateTime.DateTime(1905,9,1)],
[mx.DateTime.DateTime(1906,8,24),mx.DateTime.DateTime(1906,8,31)],
[mx.DateTime.DateTime(1907,8,23),mx.DateTime.DateTime(1907,8,30)],
[mx.DateTime.DateTime(1908,8,20),mx.DateTime.DateTime(1908,8,28)],
[mx.DateTime.DateTime(1909,8,27),mx.DateTime.DateTime(1909,9,3)],
[mx.DateTime.DateTime(1910,8,25),mx.DateTime.DateTime(1910,9,2)],
[mx.DateTime.DateTime(1911,8,24),mx.DateTime.DateTime(1911,9,1)],
[mx.DateTime.DateTime(1912,8,22),mx.DateTime.DateTime(1912,8,30)],
[mx.DateTime.DateTime(1913,8,20),mx.DateTime.DateTime(1913,8,28)],
[mx.DateTime.DateTime(1914,8,26),mx.DateTime.DateTime(1914,9,4)],
[mx.DateTime.DateTime(1915,8,25),mx.DateTime.DateTime(1915,9,3)],
[mx.DateTime.DateTime(1916,8,23),mx.DateTime.DateTime(1916,9,1)],
[mx.DateTime.DateTime(1917,8,22),mx.DateTime.DateTime(1917,8,31)],
[mx.DateTime.DateTime(1918,8,21),mx.DateTime.DateTime(1918,8,30)],
[mx.DateTime.DateTime(1919,8,20),mx.DateTime.DateTime(1919,8,29)],
[mx.DateTime.DateTime(1920,8,25),mx.DateTime.DateTime(1920,9,3)],
[mx.DateTime.DateTime(1921,8,24),mx.DateTime.DateTime(1921,9,2)],
[mx.DateTime.DateTime(1922,8,23),mx.DateTime.DateTime(1922,9,1)],
[mx.DateTime.DateTime(1923,8,22),mx.DateTime.DateTime(1923,8,31)],
[mx.DateTime.DateTime(1924,8,20),mx.DateTime.DateTime(1924,8,29)],
[mx.DateTime.DateTime(1925,8,26),mx.DateTime.DateTime(1925,9,4)],
[mx.DateTime.DateTime(1926,8,25),mx.DateTime.DateTime(1926,9,3)],
[mx.DateTime.DateTime(1927,8,24),mx.DateTime.DateTime(1927,9,2)],
[mx.DateTime.DateTime(1928,8,22),mx.DateTime.DateTime(1928,8,31)],
[mx.DateTime.DateTime(1929,8,21),mx.DateTime.DateTime(1929,8,30)],
[mx.DateTime.DateTime(1930,8,20),mx.DateTime.DateTime(1930,8,29)],
[mx.DateTime.DateTime(1931,8,26),mx.DateTime.DateTime(1931,9,4)],
[mx.DateTime.DateTime(1932,8,24),mx.DateTime.DateTime(1932,9,2)],
[mx.DateTime.DateTime(1933,8,23),mx.DateTime.DateTime(1933,9,1)],
[mx.DateTime.DateTime(1934,8,22),mx.DateTime.DateTime(1934,8,31)],
[mx.DateTime.DateTime(1935,8,21),mx.DateTime.DateTime(1935,8,30)],
[mx.DateTime.DateTime(1936,8,26),mx.DateTime.DateTime(1936,9,4)],
[mx.DateTime.DateTime(1937,8,25),mx.DateTime.DateTime(1937,9,3)],
[mx.DateTime.DateTime(1938,8,24),mx.DateTime.DateTime(1938,9,2)],
[mx.DateTime.DateTime(1939,8,23),mx.DateTime.DateTime(1939,9,1)],
[mx.DateTime.DateTime(1940,8,21),mx.DateTime.DateTime(1940,8,30)],
[mx.DateTime.DateTime(1941,8,20),mx.DateTime.DateTime(1941,8,29)],
[mx.DateTime.DateTime(1946,8,21),mx.DateTime.DateTime(1946,8,30)],
[mx.DateTime.DateTime(1947,8,22),mx.DateTime.DateTime(1947,8,29)],
[mx.DateTime.DateTime(1948,8,25),mx.DateTime.DateTime(1948,9,3)],
[mx.DateTime.DateTime(1949,8,24),mx.DateTime.DateTime(1949,9,2)],
[mx.DateTime.DateTime(1950,8,25),mx.DateTime.DateTime(1950,9,1)],
[mx.DateTime.DateTime(1951,8,25),mx.DateTime.DateTime(1951,9,3)],
[mx.DateTime.DateTime(1952,8,23),mx.DateTime.DateTime(1952,9,1)],
[mx.DateTime.DateTime(1953,8,29),mx.DateTime.DateTime(1953,9,7)],
[mx.DateTime.DateTime(1954,8,28),mx.DateTime.DateTime(1954,9,6)],
[mx.DateTime.DateTime(1955,8,27),mx.DateTime.DateTime(1955,9,5)],
[mx.DateTime.DateTime(1956,8,24),mx.DateTime.DateTime(1956,9,2)],
[mx.DateTime.DateTime(1957,8,23),mx.DateTime.DateTime(1957,9,1)],
[mx.DateTime.DateTime(1958,8,22),mx.DateTime.DateTime(1958,8,31)],
[mx.DateTime.DateTime(1959,8,28),mx.DateTime.DateTime(1959,9,6)],
[mx.DateTime.DateTime(1960,8,26),mx.DateTime.DateTime(1960,9,4)],
[mx.DateTime.DateTime(1961,8,25),mx.DateTime.DateTime(1961,9,3)],
[mx.DateTime.DateTime(1962,8,17),mx.DateTime.DateTime(1962,8,26)],
[mx.DateTime.DateTime(1963,8,16),mx.DateTime.DateTime(1963,8,25)],
[mx.DateTime.DateTime(1964,8,21),mx.DateTime.DateTime(1964,8,30)],
[mx.DateTime.DateTime(1965,8,20),mx.DateTime.DateTime(1965,8,29)],
[mx.DateTime.DateTime(1966,8,19),mx.DateTime.DateTime(1966,8,28)],
[mx.DateTime.DateTime(1967,8,18),mx.DateTime.DateTime(1967,8,27)],
[mx.DateTime.DateTime(1968,8,16),mx.DateTime.DateTime(1968,8,26)],
[mx.DateTime.DateTime(1969,8,15),mx.DateTime.DateTime(1969,8,24)],
[mx.DateTime.DateTime(1970,8,21),mx.DateTime.DateTime(1970,8,30)],
[mx.DateTime.DateTime(1971,8,20),mx.DateTime.DateTime(1971,8,29)],
[mx.DateTime.DateTime(1972,8,18),mx.DateTime.DateTime(1972,8,28)],
[mx.DateTime.DateTime(1973,8,17),mx.DateTime.DateTime(1973,8,27)],
[mx.DateTime.DateTime(1974,8,16),mx.DateTime.DateTime(1974,8,26)],
[mx.DateTime.DateTime(1975,8,15),mx.DateTime.DateTime(1975,8,24)],
[mx.DateTime.DateTime(1976,8,18),mx.DateTime.DateTime(1976,8,29)],
[mx.DateTime.DateTime(1977,8,18),mx.DateTime.DateTime(1977,8,28)],
[mx.DateTime.DateTime(1978,8,17),mx.DateTime.DateTime(1978,8,27)],
[mx.DateTime.DateTime(1979,8,16),mx.DateTime.DateTime(1979,8,26)],
[mx.DateTime.DateTime(1980,8,14),mx.DateTime.DateTime(1980,8,24)],
[mx.DateTime.DateTime(1981,8,13),mx.DateTime.DateTime(1981,8,23)],
[mx.DateTime.DateTime(1982,8,12),mx.DateTime.DateTime(1982,8,22)],
[mx.DateTime.DateTime(1983,8,10),mx.DateTime.DateTime(1983,8,20)],
[mx.DateTime.DateTime(1984,8,15),mx.DateTime.DateTime(1984,8,25)],
[mx.DateTime.DateTime(1985,8,15),mx.DateTime.DateTime(1985,8,25)],
[mx.DateTime.DateTime(1986,8,14),mx.DateTime.DateTime(1986,8,24)],
[mx.DateTime.DateTime(1987,8,20),mx.DateTime.DateTime(1987,8,30)],
[mx.DateTime.DateTime(1988,8,18),mx.DateTime.DateTime(1988,8,28)],
[mx.DateTime.DateTime(1989,8,17),mx.DateTime.DateTime(1989,8,27)],
[mx.DateTime.DateTime(1990,8,15),mx.DateTime.DateTime(1990,8,26)],
[mx.DateTime.DateTime(1991,8,14),mx.DateTime.DateTime(1991,8,25)],
[mx.DateTime.DateTime(1992,8,20),mx.DateTime.DateTime(1992,8,30)],
[mx.DateTime.DateTime(1993,8,19),mx.DateTime.DateTime(1993,8,29)],
[mx.DateTime.DateTime(1994,8,11),mx.DateTime.DateTime(1994,8,21)],
[mx.DateTime.DateTime(1995,8,10),mx.DateTime.DateTime(1995,8,20)],
[mx.DateTime.DateTime(1996,8,8),mx.DateTime.DateTime(1996,8,18)],
[mx.DateTime.DateTime(1997,8,7),mx.DateTime.DateTime(1997,8,17)],
[mx.DateTime.DateTime(1998,8,13),mx.DateTime.DateTime(1998,8,23)],
[mx.DateTime.DateTime(1999,8,12),mx.DateTime.DateTime(1999,8,22)],
[mx.DateTime.DateTime(2000,8,10),mx.DateTime.DateTime(2000,8,20)],
[mx.DateTime.DateTime(2001,8,9),mx.DateTime.DateTime(2001,8,19)],
[mx.DateTime.DateTime(2002,8,8),mx.DateTime.DateTime(2002,8,18)],
[mx.DateTime.DateTime(2003,8,7),mx.DateTime.DateTime(2003,8,17)],
[mx.DateTime.DateTime(2004,8,12),mx.DateTime.DateTime(2004,8,22)],
[mx.DateTime.DateTime(2005,8,11),mx.DateTime.DateTime(2005,8,21)],
[mx.DateTime.DateTime(2006,8,10),mx.DateTime.DateTime(2006,8,20)],
[mx.DateTime.DateTime(2007,8,9),mx.DateTime.DateTime(2007,8,19)],
[mx.DateTime.DateTime(2008,8,7),mx.DateTime.DateTime(2008,8,17)],
[mx.DateTime.DateTime(2009,8,13),mx.DateTime.DateTime(2009,8,23)],
[mx.DateTime.DateTime(2010,8,12),mx.DateTime.DateTime(2010,8,22)],
[mx.DateTime.DateTime(2011,8,11),mx.DateTime.DateTime(2011,8,21)],
]

import numpy
import numpy.ma

#avgT = numpy.ma.zeros( (2012-1880) )
precip = numpy.ma.zeros( (2012-1880) )
precip[:] = -0.000000001
#heatcnt = numpy.ma.zeros( (2012-1880) )
#heatcnt[:] = -1

cnts = numpy.zeros( (12) )
hits = numpy.zeros( (12) )
rains = numpy.zeros( (12) )
total = numpy.zeros( (12) )

dwpfs = open('dwpf.txt', 'w')

for sts, ets in FAIRS:
  #if sts.year < 1933:
  #  continue
  ccursor.execute("""
  SELECT day, precip from alldata where stationid = 'ia2203' and
  day >= '%s' and day <= '%s' ORDER by day ASC
  """ % (sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d")))
  i = 0
  for row in ccursor:
    if row[1] > 0.04:
      hits[i] += 1
    if row[1] > 0.00:
      total[i] += row[1]
      rains[i] += 1
      precip[sts.year-1880] += row[1]
    else:
      precip[sts.year-1880] += 0.001
    cnts[i] += 1
    i += 1
  #if row[0] > 50:
  #  avgT[sts.year-1880] = row[0]

  # Heat index
  if sts.year < 1933:
    continue
  acursor.execute("""
   SELECT date(valid) as d, max(dwpf), min(dwpf) from t%s 
   WHERE station = 'DSM' and tmpf > 0 and dwpf > 0 and 
   valid BETWEEN '%s 00:00' and '%s 23:59' GROUP by d ORDER by d ASC
  """ % (sts.year, sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d")))
  keys = {}
  cnt = 0
  data = ['M']*12
  data2 = ['M']*12
  cnt = 0
  for row in acursor:
    data[cnt] = str(row[1])
    data2[cnt] = str(row[2])
    cnt += 1
    #h = mesonet.heatidx(row[1], mesonet.relh(row[1], row[2]))
    #if h >= 90:
    #  keys[ row[0].strftime("%Y%m%d%H") ] = 1
 
  dwpfs.write("%s,%s,%s\n" % (`sts.year`, ",".join(data), ",".join(data2)))
  #if cnt > 50:
  #  heatcnt[sts.year-1880] = len(keys.keys())

dwpfs.close()

decades = numpy.ma.zeros( (2012-1880) )

for decade in range(1880,2020,10):
  avg = numpy.ma.average( precip[decade-1880:decade-1880+10] )
  decades[decade-1880:decade-1880+10] = avg

#avgT[2011-1880] = 88
#avgT.mask = numpy.where(avgT == 0, True, False)
#heatcnt.mask = numpy.where(heatcnt == -1, True, False)
avgP = numpy.ma.average(precip)
precip = numpy.where(precip < 0, 9, precip)

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)
bars = ax.bar(numpy.arange(1880,2012)-0.4, precip, edgecolor='r', facecolor='r')
for bar in bars:
  if bar.get_height() == 9:
    bar.set_facecolor("#EEEEEE")
    bar.set_edgecolor("#EEEEEE")
  elif bar.get_height() > avgP:
    bar.set_facecolor("b")
    bar.set_edgecolor("b")
ax.plot(numpy.arange(1880,2012),decades, color='black', label='Decade Average')
bars[-1].set_facecolor('blue')
bars[-1].set_edgecolor('blue')
ax.set_xlim(1892.5,2011.5)
#ax.set_ylim(numpy.ma.min(avgT) - 3, numpy.ma.max(avgT) + 3)
ax.grid(True)
ax.legend(loc=2)
ax.set_title("Iowa State Fair Precipitation")
ax.set_ylabel("Total Precipitation [inch]")
ax.set_xlabel("*2011 data thru 17 August")

ax2 = fig.add_subplot(212)
ax2.bar(numpy.arange(1,13)-0.4, hits / cnts * 100. )
ax2.set_ylabel("Frequency of 0.05+ inches [%]")
#ax2.bar(numpy.arange(1880,2012)-0.4, heatcnt, edgecolor='r', facecolor='r')
ax2.set_xlim(0.5,11.5)
ax2.set_xticks( numpy.arange(1,12) )
ax2.set_xticklabels( numpy.arange(1,12) )
#ax2.set_yticks( numpy.arange(0,5*24,24))
ax2.grid(True)
#ax2.set_ylabel("Hours with\n Heat Index over 90")
ax2.set_xlabel("Day of Fair")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
