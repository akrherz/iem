import psycopg2
import numpy as np

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

maxes = np.zeros((200,))  # -60 to 140

cursor.execute("""SELECT day, high from alldata_ia WHERE 
 station = 'IA2203' ORDER by day ASC""")

last = -99
running = 1
for row in cursor:
    if row[1] == last:
        running += 1
    else:
        if running > maxes[last+60]:
            maxes[last+60] = running
        if running > 4:
            print row
        running = 1
        last = row[1]

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

bars = ax.bar(np.arange(-60,140)-0.4, maxes, fc='r', ec='r')
        
ax.text( 36, 4.8, "7-11 Mar 1962" )
ax.text( 87, 4.8, "28 Jul - 1 Aug 2003" )
ax.set_xlim(-20,120)
ax.set_title("1880-28 Aug 2013 Des Moines Consecutive Days at High Temp")
ax.set_ylabel("Consecutive Days")
ax.set_xlabel("High Temperature $^\circ$F")
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')