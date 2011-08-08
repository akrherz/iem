import matplotlib.pyplot as plt
import numpy
from scipy import stats


data = """1951 14.6203301847
1952 14.7525724024
1953 13.7012004852
1954 12.6861538738
1955 16.0190146416
1956 14.3645331264
1957 11.8256201968
1958 15.4606793076
1959 15.1960272342
1960 13.031668961
1961 13.9352092519
1962 12.1059129015
1963 12.1269645169
1964 13.5482540354
1965 13.0366506055
1966 12.9079846665
1967 13.4936179966
1968 14.4740398973
1969 14.1783189029
1970 13.8691021129
1971 13.166282326
1972 14.5459212363
1973 13.835189864
1974 12.9683567211
1975 13.9612555504
1976 12.9710864276
1977 14.9708809331
1978 14.8850884289
1979 15.7486870885
1980 15.6400222331
1981 15.7769229263
1982 14.1498511657
1983 13.7509377673
1984 14.1931707039
1985 13.8350110501
1986 14.6822733805
1987 15.1202119887
1988 14.8442778736
1989 15.4766663909
1990 15.0378961116
1991 14.4752450287
1992 14.7258993238
1993 15.6743917614
1994 16.8363414705
1995 15.7376695424
1996 14.4159207121
1997 13.6545738205
1998 13.1685780361
1999 15.2304945514
2000 13.3567638695
2001 13.1648657843
2002 14.1233820468
2003 14.8195521906
2004 14.9218328297
2005 15.3806759045
2006 15.7159809023
2007 12.3090678826
2008 13.8108404353
2009 12.1449939907
2010 13.9541616663
2011 14.9761717767"""

years = []
vals = []
for line in data.split("\n"):
    tokens = line.split()
    vals.append( float(tokens[1]) )
    years.append( float(tokens[0]) )

vals = numpy.array( vals )
years = numpy.array( years )
h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(years, vals)
print h_slope, h_r_value ** 2, intercept
trend = numpy.array( vals )
for yr in range(1951,2012):
    trend[yr-1951] = intercept + (yr) * h_slope

fig = plt.figure(figsize=(6,8))
ax = fig.add_subplot(211)
ax.set_xlim(1950.5,2012)
ax.bar(years, vals)
ax.plot( years -0.4, trend, color='r')
ax.text(1951, 16.3, 'Slope: %.2f/decade R^2: %.2f' % (h_slope * 10, h_r_value**2))
ax.set_title("Washington National KDCA\n Average July Surface Mixing Ratio")
ax.set_ylabel("Mixing Ratio [g/kg]")
ax.set_ylim(10,17)
"""
ax2 = fig.add_subplot(312)

bars = ax2.bar(years-0.4, vals - numpy.average(vals), edgecolor='b', facecolor='b')
for bar in bars:
    if bar.get_y() < 0:
        bar.set_edgecolor('r')
        bar.set_facecolor('r')
ax2.set_title("Mid-West July Departure from Average")
ax2.set_ylabel("Mixing Ration [g/kg]")
#ax2.set_ylim(8,14)
ax2.grid(True)
ax2.set_xlim(1950.5,2011.5)
"""
ax3 = fig.add_subplot(212)

bars = ax3.bar(years-0.4, vals - trend, edgecolor='b', facecolor='b')
for bar in bars:
    if bar.get_y() < 0:
        bar.set_edgecolor('r')
        bar.set_facecolor('r')
        
ax3.set_title("Departure from Trend")
ax3.set_ylabel("Mixing Ratio [g/kg]")
ax3.grid(True)
ax3.set_xlim(1950.5,2011.5)
#ax3.set_xlabel("*2011 total thru 26 July")
fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')


