import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT distinct extract(doy from day), year from alldata_ia 
 WHERE high > 99 and year > 1880 and year < 2012
""")
years = []
doy = []
cnt = [0]*(2012-1880)
for row in ccursor:
    years.append( row[1] )
    doy.append( row[0] )
    cnt[row[1]-1880] += 1
    
import matplotlib.pyplot as plt

fig, ax = plt.subplots(2,1)

ax[0].scatter(years, doy)
ax[0].set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[0].set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[0].set_ylim(91,305)
ax[0].grid(True)
ax[0].set_title("Days with at least one 100$^{\circ}\mathrm{F}$ Report in Iowa")
ax[0].set_xlim(1890,2012)

ax[1].bar(range(1880,2012), cnt)
ax[1].grid(True)
ax[1].set_ylabel("Days per Year")
ax[1].set_xlim(1890,2012)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')