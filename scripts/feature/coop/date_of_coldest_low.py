import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

doy = []
low = []
years = []

def r(v):
    if v < 180:
        return v+366
    return v

for year in range(1893,2013):
    ccursor.execute("""
    SELECT doy, low from (
    select extract(doy from day) as doy, low, rank() over (order by low ASC) from alldata_ia 
    where station = 'IA0200' and day > '%s-09-01' and day < '%s-05-01') as foo
    WHERE rank = 1
    """ % (year, year+1))
    for row in ccursor:
        doy.append( r(row[0]) )
        low.append( row[1] )
        years.append( year+1)
        
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.scatter( doy[:-3], low[:-3], color='b')
ax.scatter( doy[-2:], low[-2:], color='r')
for d,l,y in zip(doy, low, years):
    if l > -6 or d > 425 or l <= -30:
        ax.text(d, l, "%s" % (y,), ha='left', va='top')
ax.set_xticks( (305,335,365, 396, 425) )
ax.set_xticklabels( ('1 Nov', '1 Dec', '1 Jan', '1 Feb', '1 Mar') )
ax.set_xlim(330,445)
ax.set_title("1893-2013 Ames Date of Coldest Winter Temperature")
ax.set_xlabel("*2013 thru 22 Jan, ties shown, selected year for January shown")
ax.set_ylabel("Coldest Temperature $^{\circ}\mathrm{F}$")
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')