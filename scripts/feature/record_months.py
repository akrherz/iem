import iemdb
coop = iemdb.connect('coop', bypass=True)
ccursor = coop.cursor()

years = []
months = []
for mo in range(1,13):
    ccursor.execute("""
    SELECT year, sum(precip) as s from alldata where stationid = 'ia2203'
    and month = %s GROUP by year ORDER by s DESC LIMIT 6
    """ % (mo,))
    for row in ccursor:
        years.append( row[0] )
        months.append( mo )
        
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(months, years)
ax.set_ylim(1893,2012)

fig.savefig('test.png')