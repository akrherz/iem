import psycopg2
import matplotlib.pyplot as plt
import numpy as np

dbconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = dbconn.cursor()

def get():
    cursor.execute("""
     SELECT d, d - lag(d) over (ORDER by d ASC) from
     
     (SELECT date((issue at time zone 'UTC') + '12 hours'::interval) as d, count(*)
     from warnings where phenomena in ('SV','TO') and significance = 'W' 
     and gtype = 'C' and substr(ugc, 1,3) = 'IAC' GROUP by d ORDER by d ASC) as foo
     
     ORDER by d ASC
    """)
    
    dates = []
    days = []
    for row in cursor:
        days.append( row[1] )
        dates.append( row[0] )
        
    events = 0
    hits = [0]*11
    sz = len(dates)
    cnt = 0
    for i, (d, dy) in enumerate(zip(dates, days)):
        if d.month in (9,10,11,12):
            cnt += 1
        if dy < 10 or d.month > 5:
            continue
        events += 1
        for j in range(i+1, i+11):
            if j >= sz:
                continue
            delta = (dates[j]-d).days
            if delta <= 10:
                print i, j, j-i, delta, dates[j], d
                hits[delta] += 1
                
    print cnt, events, hits
 
get()  
sond_events = 59.0
sond_hits = np.array([7, 8, 1, 3, 1, 2, 3, 5, 5, 4])
sond_climo = 165.0 / (30+31+30+31) / 28.0
jja_events = 35.0
jja_total = 824 / (30+31+31) / 28.0
jja_hits = np.array([14, 13, 11, 11, 8, 10, 11, 7, 9, 10])
jm_events = 96.0
jm_total = 437 / (31+28+31+31+31)
jm_hits = np.array([40, 24, 16, 21, 16, 18, 16, 11, 12, 15])
#all_events = 190.0
#all_hits = np.array([61, 45, 28, 35, 25, 30, 30, 23, 26, 29])

(fig, ax) = plt.subplots(1,1)

ax.bar( np.arange(1,11)-0.37, jm_hits / jm_events * 100.0, width=0.25,
        fc='r', label='Jan-May, n=%.0f' % (jm_events,))
ax.bar( np.arange(1,11)-0.12, jja_hits / jja_events * 100.0, width=0.25,
        fc='g', label='Jun-Aug, n=%.0f' % (jja_events,))
ax.bar( np.arange(1,11)+0.13, sond_hits / sond_events * 100.0, width=0.25,
        fc='b', label='Sept-Dec, n=%.0f' % (sond_events,))
ax.set_ylabel("Frequency [%]")
ax.set_title("After 10+ Day Period in Iowa without Severe Warnings\nFrequency of Warnings on Subsequent Days [1986-2013]")
ax.grid()
ax.set_xticks(np.arange(1,11))
ax.legend(fontsize=12)
ax.set_xlim(0.5,10.5)
ax.set_xlabel("Days (~ 7 AM to 7 AM) After Initial Severe Wx Date")

fig.savefig('test.png')
