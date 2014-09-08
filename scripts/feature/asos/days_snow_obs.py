import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

DOY = []
TMPF = []

acursor.execute("""SELECT extract(doy from valid) as doy, tmpf from
 alldata where station = 'DSM' and presentwx ~* 'SN' """)

for row in acursor:
    add = 0
    if row[0] < 180:
        add = 366
    DOY.append( row[0] + add )
    TMPF.append( row[1] )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

print len(DOY)
ax.set_title("1933-2012 Des Moines METAR Observations of Snowfall")
ax.set_xlabel("Day of Year, red square is 14 Feb 2013 Report")
ax.set_ylabel("Air Temperature @ Observation $^{\circ}\mathrm{F}$")
ax.scatter(DOY, TMPF, zorder=1)
ax.scatter(366+31+14, 40, marker='s', s=40, zorder=2, c='r')
ax.grid(True)

ax.set_xticks( (274,305,335, 365, 397, 425, 456 ,366+121) )
ax.set_xticklabels( ('Oct','Nov','Dec','Jan','Feb','Mar','Apr','May') )
ax.set_xlim(270, 366+125)


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
    