import psycopg2
import numpy as np
import datetime

gddavg = np.zeros((366), 'f')
gddmax = np.zeros((366), 'f')
gdd2013 = np.zeros((366), 'f')

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
 SELECT sday, min(g), avg(g), max(g),
 max(case when year = 2013 then g else 0 end) from
   (SELECT sday, gddxx(50,86,high,low) as g, year from alldata_ia 
    where station = 'IA0200') as foo
 GROUP by sday
""")

for row in cursor:
    ts = datetime.datetime.strptime('2000%s' % (row[0],), '%Y%m%d')
    doy = int(ts.strftime("%j")) - 1
    gddavg[doy] = row[2]
    gddmax[doy] = row[3]
    if row[4] > 0:
        gdd2013[doy] = row[4]
        

may1 = int(datetime.datetime(2000,5,1).strftime("%j")) - 1
aug19 = int(datetime.datetime(2000,8,19).strftime("%j")) - 1

jdays = []
maxout = []
d120 = []
for jday in range(may1+1,aug19): 
    jdays.append( jday )
    normal = np.sum(gddavg[may1:jday])
    d2013 = np.sum(gdd2013[may1:jday])
    
    departure = d2013 - normal
    i = jday
    while departure < 0 and i < 366:
        departure += (gddmax[i] - gddavg[i])
        i += 1
    maxout.append(i)
    
    departure = d2013 - normal
    i = jday
    while departure < 0 and i < 366:
        departure += (0.2 * gddavg[i])
        i += 1
    d120.append(i)
    
maxout = np.array(maxout)
d120 = np.array(d120)
jdays = np.array(jdays)
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.bar(jdays, d120-jdays, bottom=jdays, zorder=2, fc='g', ec='g', label='120% of average')
ax.bar(jdays, maxout-jdays, bottom=jdays, zorder=3, fc='r', ec='r', label='Daily Maximum')
#ax.plot([may1,aug19],[may1,aug19])
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335) )
ax.set_yticklabels( ('Jan','Feb','Mar','Apr','May 1','Jun 1','Jul 1','Aug 1','Sep 1','Oct 1','Nov 1','Dec') )
ax.set_xlim(may1,244)
ax.set_ylim(may1,279)
ax.set_ylabel("Date to reach average GDDs")
ax.set_xlabel("Date this 2013")
ax.set_title("Ames Growing Degree Days (50/86)\nScenarios to recover 2013 deficit since 1 May")
ax.legend(loc=4)
ax.grid(True)

ax.annotate("With 120% GDDs accumulated\ngoing foward, we'd reach average\naround 1 October", 
            xy=(aug19, 272),  xycoords='data',
                xytext=(130, 240), textcoords='data', color='white',
                bbox=dict(boxstyle="round", fc="g"),
                arrowprops=dict(arrowstyle="->",
                connectionstyle="arc,angleA=0,armA=30,rad=10"))

ax.annotate("With daily record heat\ngoing foward, we'd reach average\njust after 1 September", 
            xy=(aug19, 247),  xycoords='data',
                xytext=(130, 210), textcoords='data', color='k',
                bbox=dict(boxstyle="round", fc="r"),
                arrowprops=dict(arrowstyle="->",
                connectionstyle="arc,angleA=0,armA=30,rad=10"))


fig.savefig('test.png')
