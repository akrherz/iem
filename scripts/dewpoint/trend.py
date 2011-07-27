import matplotlib.pyplot as plt
import numpy
from scipy import stats


data = """1951 11.9863869622
1952 11.108382605
1953 11.5853054449
1954 11.1559573561
1955 12.6693528146
1956 10.9837893397
1957 12.8166256472
1958 11.5344645455
1959 10.905883275
1960 10.717256926
1961 10.8855850995
1962 11.2796453759
1963 11.6091202945
1964 11.4959031343
1965 11.1951399595
1966 12.2388582677
1967 10.4853985831
1968 11.0441241413
1969 12.3349791393
1970 11.1161470413
1971 9.93843562901
1972 10.8754942194
1973 11.1853452399
1974 10.7842404395
1975 11.3755920902
1976 10.913413018
1977 11.7949321866
1978 11.4146992564
1979 11.8491956964
1980 11.2548172474
1981 12.1052348986
1982 12.0273614302
1983 12.3087400571
1984 10.6149595231
1985 10.3616556153
1986 12.3357633129
1987 12.5107895583
1988 10.9948050231
1989 11.5943914279
1990 10.8887813985
1991 10.9766712412
1992 10.7576027513
1993 12.2067835182
1994 11.142118834
1995 11.773172766
1996 11.3794235513
1997 12.0148351416
1998 12.6486718655
1999 13.1981577724
2000 12.1266599745
2001 12.6959411427
2002 12.5585226342
2003 11.6936769336
2004 11.8962703273
2005 12.2605459765
2006 12.6025145873
2007 11.7487804964
2008 11.6363251582
2009 10.5443745852
2010 13.2057145238
2011 13.7072410434"""

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

fig = plt.figure(figsize=(6,9))
ax = fig.add_subplot(311)
ax.set_xlim(1950.5,2011.5)
ax.bar(years, vals)
ax.plot( years -0.4, trend, color='r')
ax.text(1951, 13.3, 'Slope: %.2f/decade R^2: %.1f' % (h_slope * 10, h_r_value**2))
ax.set_title("Mid-West Average July Surface Mixing Ratio")
ax.set_ylabel("Mixing Ration [g/kg]")
ax.set_ylim(8,14)

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

ax3 = fig.add_subplot(313)

bars = ax3.bar(years-0.4, vals - trend, edgecolor='b', facecolor='b')
for bar in bars:
    if bar.get_y() < 0:
        bar.set_edgecolor('r')
        bar.set_facecolor('r')
        
ax3.set_title("Mid-West July Departure from Trend")
ax3.set_ylabel("Mixing Ration [g/kg]")
ax3.grid(True)
ax3.set_xlim(1950.5,2011.5)

fig.savefig('test.png')