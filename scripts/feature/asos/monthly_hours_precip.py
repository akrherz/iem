import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import iemplot
import matplotlib.patheffects as PathEffects


ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()

def get2013():
    acursor.execute("""
        SELECT month, count(*)  from 
        (SELECT distinct to_char(valid, 'YYYYMMDDHH24') as d, 
        extract(month from valid) as month from alldata 
        where station = 'DSM' and valid > '2013-01-01' 
        and valid < '2014-01-01' and p01i > 0) as foo
        GROUP by month ORDER by month ASC
        """)
    moclimo = []
    for row in acursor:
        moclimo.append( float(row[1]) )
    return moclimo

def get_moclimo():
    acursor.execute("""
        SELECT month, count(*) / 40.0 from 
        (SELECT distinct to_char(valid, 'YYYYMMDDHH24') as d, 
        extract(month from valid) as month from alldata 
        where station = 'DSM' and valid < '2013-01-01' 
        and valid > '1973-01-01' and p01i > 0) as foo
        GROUP by month ORDER by month ASC
        """)
    moclimo = []
    for row in acursor:
        moclimo.append( float(row[1]) )
    return moclimo

moclimo = get_moclimo()
m2013 = get2013()
print m2013

(fig, ax) = plt.subplots(1,1)
ax.bar( np.arange(1,13)-0.4, moclimo, label='Climatology')
bars = ax.bar( np.arange(1,10)-0.2, m2013, width=0.4, fc='yellow', label='2013', zorder=2)
for i, bar in enumerate(bars):
    txt = ax.text(i+1, m2013[i]+2, "%.0f" % (m2013[i],), ha='center')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                     foreground="yellow")])

ax.set_xlim(0.5,12.5)
ax.legend()
ax.grid(True)
ax.set_xticks(np.arange(1,13))
ax.set_xticklabels(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                "Oct", "Nov", "Dec"))
ax.set_xlabel("* 2013 thru 17 September")
ax.set_ylabel("Hours")
ax.set_yticks(np.arange(0,24*4 +1,12))
ax.set_title("Des Moines Hours with Measurable Precipitation by Month")
fig.savefig('test.ps')
iemplot.makefeature('test')