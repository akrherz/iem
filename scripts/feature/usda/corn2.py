
# VT 1135
# R2 1660
import mx.DateTime
import datetime
import iemdb
import pandas as pd
import numpy as np
from scipy import stats
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()


ccursor.execute("""
WITH climo as (
  SELECT extract(month from valid) as month, sum(precip) from climate51 where
  station= 'IA0000' GROUP by month),
  
obs as (
  SELECT year, month, sum(precip) from alldata_ia where
  station = 'IA0000' and month in (5,6,7,8) and year > 1950 and year < 2014
  GROUP by year, month),
  
combo as (
  SELECT obs.year, obs.month, obs.sum - climo.sum as diff from obs JOIN climo on
 (obs.month = climo.month) )
 
SELECT year, month, diff, rank() OVER (PARTITION by year ORDER by diff DESC )
 from combo 
""")
res = []
for row in ccursor:
    if row[3] == 1:
        res.append( dict(year=row[0], month=row[1], wxdeparture=row[2],
                         yielddeparture=0))

df = pd.DataFrame(res)

years = []
yields = []
for line in open('/home/akrherz/Downloads/corn.csv'):
    tokens = line.split(",")
    years.insert(0, float(tokens[1]))
    yields.insert(0, float(tokens[-2]))
years = np.array(years)
yields = np.array(yields)

h_slope, intercept, r_value, p_value, std_err = stats.linregress(years, yields)
barcolors = []
departures = []
for year in years:
    expected = h_slope * year + intercept
    departures.append( (yields[year - 1951] - expected) / expected * 100.0 )
    df['yielddeparture'][df['year']==year] = departures[-1]

import matplotlib.pyplot as plt
fig,ax = plt.subplots(2,1)

ax[0].scatter(years, yields)
ax[0].set_xlim(1950,2015)
ax[0].grid(True)
ax[0].set_ylabel("Corn Grain Yield bu/acre")
ax[0].set_title("Iowa Corn Yield Departure from Trend & Wettest Month")
ax[0].plot(years, h_slope * years + intercept)

bars = ax[1].scatter( df['wxdeparture'][df['month']==5], 
                      df['yielddeparture'][df.month==5], marker='v',
                      label='May', c='r', s=50)
bars = ax[1].scatter( df['wxdeparture'][df['month']==6], 
                      df['yielddeparture'][df.month==6], marker='+',
                      label='June', c='b', s=50)
bars = ax[1].scatter( df['wxdeparture'][df['month']==7], 
                      df['yielddeparture'][df.month==7], marker='o',
                      label='July', c='g', s=50)
bars = ax[1].scatter( df['wxdeparture'][df['month']==8], 
                      df['yielddeparture'][df.month==8], marker='s', 
                      label='August', s=50)
ax[1].legend(ncol=1, prop={'size': 10}, scatterpoints=1)
ax[1].set_ylim(-50,50)
ax[1].set_xlabel("Wettest Monthly Departure for Year [inch]")
ax[1].set_ylabel("Yield Departure from Trendline [%]", fontsize=10)
ax[1].grid(True)
for i, row in df.iterrows():
    if row['wxdeparture'] > 4 or row['yielddeparture'] < -20 or row['yielddeparture'] > 20:
        ax[1].text(row['wxdeparture'] + 0.1, row['yielddeparture'], '%.0f' % (row['year'], ),
                   va='center')
ax[1].plot([5.7, 5.7], [-50,50], '-.')
ax[1].text(5.8, -30, 'Jun\n2014', color='b')

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
