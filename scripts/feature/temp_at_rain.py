import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute("""
    SELECT dwpf, extract(doy from valid), p01m / 25.4 from alldata 
    where station = 'DSM' 
    and p01m >= (0.05 * 25.4)
    and valid > '1996-01-01' and tmpf >= -50
""")

tmpf = []
doy = []
precip = []
for row in acursor:
    tmpf.append( row[0] )
    doy.append( row[1] )
    precip.append( row[2] )
    
import iemplot
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_xlim(0,366)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
ax.set_ylabel('Dew Point Temperature $^{\circ}\mathrm{F}$')
ax.set_title('Des Moines Dew Point / Precipitation [1996-2010]\nwhen reporting > 0.05" precip')
ax.scatter( doy, tmpf )

ax2 = fig.add_subplot(212)
ax2.set_ylim(0, 2.5)
ax2.set_xlabel('Dew Point Temperature $^{\circ}\mathrm{F}$')
ax2.set_ylabel('Hourly Precip [inch]')
ax2.scatter( tmpf, precip )
ax2.grid(True)
fig.savefig('test.ps')
iemplot.makefeature('test')