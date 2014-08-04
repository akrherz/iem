import psycopg2
import numpy as np
from scipy import stats
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

years = []
rain = []
temp = []
ccursor.execute("""
  WITH precip as (
  SELECT year, sum(precip) * 25.4 as rain from alldata_ia where
  station = 'IA0000' and month in (5,6) GROUP by year),
  temps as (
  SELECT year, sum(case when high > 93 then 1 else 0 end) as t from alldata_ia
  WHERE station = 'IA0000' and month in (7,8) GROUP by year)
  
  SELECT p.year, rain, t from precip p JOIN temps t on (t.year = p.year)
  WHERE t.year < 2014

""")
for row in ccursor:
    years.append( row[0] )
    temp.append( row[2] )
    rain.append( row[1] )
    
years = np.array( years )
temp = np.array( temp )
rain = np.array( rain )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1, 1)

ax.scatter(rain, temp, marker='s', facecolor='b', edgecolor='b')
ax.set_title("1893-2013 Iowa Areal Average\nMay-June Rainfall + July-August Hot Days (> 93$^\circ$F)")
ax.grid(True)

h_slope, intercept, r_value, p_value, std_err = stats.linregress(rain,
                                                                 temp)
y = h_slope * np.arange(50,401,50) + intercept
ax.plot(np.arange(50,401,50), y, lw=2, color='r')
print intercept, h_slope
ax.text(325,10, r"Slope=%.2f days/mm" % (h_slope,))
ax.text(325,7, r"R$^2$=%.2f" % (r_value ** 2,) )
ax.set_ylim(bottom=-3)
ax.set_ylabel("Number July-August Days > 93$^\circ$F")
ax.set_xlabel("May-June Precipitation [mm]")
#ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
#ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
#ax.set_xlim(0,140)
ax.set_xlabel("* 2014 thru 25 March")
fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')