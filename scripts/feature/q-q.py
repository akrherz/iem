import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

years = {}
ccursor.execute("""
    select year, rank()  over (ORDER by sum ASC), sum, 
        rank() over (ORDER by avg DESC), avg from 
    (select year, sum(precip), avg((high+low)/2.0) from alldata_ia 
    where station = 'IA0000' and month in (6,7,8) and year < 2012 GROUP by year) as foo
""")
for row in ccursor:
    years[row[0]] = {'prank': row[1], 'precip': row[2],
                     'trank': row[3], 'avgt': row[4]}
    
ccursor.execute("""
    select year, rank()  over (ORDER by sum ASC), sum, 
        rank() over (ORDER by avg DESC), avg from 
    (select year, sum(precip), avg((high+low)/2.0) from alldata_ia 
    where station = 'IA0000' and month in (9,10,11) and year < 2012 GROUP by year) as foo
""")
for row in ccursor:
    years[row[0]]['fall_prank'] = row[1]
    years[row[0]]['fall_precip'] = row[2]
    years[row[0]]['fall_trank'] = row[3]
    years[row[0]]['fall_avgt'] = row[4]

ccursor.execute("""
    select year2, rank()  over (ORDER by sum ASC), sum, 
        rank() over (ORDER by avg DESC), avg from 
    (select extract(year from day - '3 months'::interval) as year2, sum(precip), avg((high+low)/2.0) from alldata_ia 
    where station = 'IA0000' and month in (12,1,2) and day >= '1893-11-01' GROUP by year2) as foo
""")
for row in ccursor:
    years[row[0]]['winter_prank'] = row[1]
    years[row[0]]['winter_precip'] = row[2]
    years[row[0]]['winter_trank'] = row[3]
    years[row[0]]['winter_avgt'] = row[4]

one = []
two = [] 
for year in range(1893,2012):
    print '%s,%s,%.2f,%s,%.1f,%s,%.2f,%s,%.1f,%s,%.2f,%s,%.1f' % (year,
        years[year]['prank'], years[year]['precip'],
        years[year]['trank'], years[year]['avgt'],
        years[year]['fall_prank'], years[year]['fall_precip'],
        years[year]['fall_trank'], years[year]['fall_avgt'],
        years[year]['winter_prank'], years[year]['winter_precip'],
        years[year]['winter_trank'], years[year]['winter_avgt']
        )

    one.append(years[year]['prank']  )
    two.append(years[year]['fall_trank']  )

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)    

ax.scatter(one, two)

fig.savefig('test.png')