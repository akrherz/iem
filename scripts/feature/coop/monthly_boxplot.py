import psycopg2
import calendar
import matplotlib.pyplot as plt
CONN = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = CONN.cursor()

data = []
for i in range(12):
    data.append([])

cursor.execute("""SELECT month, high - low from alldata_ia where
  station = 'IA0200' """)
for row in cursor:
    data[row[0]-1].append(row[1])

(fig, ax) = plt.subplots(1, 1)

ax.boxplot(data)
ax.set_ylabel("Daily High & Low Temp Diff $^\circ$F")
ax.set_ylim(bottom=0)
ax.grid(True)
ax.set_xticklabels(calendar.month_abbr[1:])
ax.set_title("1893-2013 Ames Daily Hi-Lo Temp Difference")

fig.savefig('test.png')
