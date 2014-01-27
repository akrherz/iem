import psycopg2
import numpy as np
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
WITH obs as (
 SELECT year, sum(precip) from alldata_ia where station = 'IAC005' and
 month in (7,8,9) GROUP by year
 ),
 future as (
 SELECT year, avg((high+low)/2.) from alldata_ia where station = 'IAC005'
 and month in (1,2,3) GROUP by year
 )
 
 SELECT obs.year, obs.sum, future.avg from obs JOIN future on 
 (future.year - 1 = obs.year)
 
""")

precip = []
temps = []
for row in cursor:
    temps.append( row[2])
    precip.append( row[1])
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)
ax.scatter(temps, precip)

fig.savefig('test.png')