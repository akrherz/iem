import iemdb, iemplot
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ts = []
d2012s = []
ms = []
ys = []
for thres in range(40,85):
    ccursor.execute("""
    select year, count(*) from alldata_ia where station = 'IA2203' 
    and high >= %s GROUP by year 
    ORDER by count DESC
    """ % (thres,))
    m = None
    years = []
    d2012 = None
    for row in ccursor:
        if m is None:
            m = row[1]
        if m == row[1]:
            years.append( `row[0]` )
        if row[0] == 2012:
            d2012 = row[1]
    print '%s %s %s %s' % (thres, d2012, m, ",".join(years))
    ts.append( thres )
    d2012s.append( d2012 )
    ms.append( m )
    ys.append( ",".join(years) )
    
import numpy
import matplotlib.pyplot as plt
(fig, ax) = plt.subplots(1,1, figsize=(9,9))

ax.barh(numpy.arange(40,85)-0.4, ms, height=0.8,  fc='#efbd47', ec='#efbd47', label='Max')
ax.barh(numpy.arange(40,85)-0.3, d2012s, height=0.6, fc='#c60c30', ec='#c60c30' , label='2012')
for (yr, val, m) in zip(ys, numpy.arange(40,85), ms):
    c = '#000000'
    if yr.find("2012") > -1:
        c = "#0000ff"
    ax.text(m+1, val, "%s - %s" % (m, yr), va='center', size=10, color=c)
ax.set_ylim(39,85)
ax.set_xlim(50,390)
ax.set_xlabel("Days per Year, thru 24 Nov 2012")
ax.set_ylabel("Daily High Temperature $^{\circ}\mathrm{F}$")
ax.set_title("Des Moines Maximum Number of Days\nAt or Above given High Temperature (1880-2012)")
ax.legend()
ax.grid()

fig.savefig('test.ps')
iemplot.makefeature('test')
