import psycopg2
import datetime
import matplotlib.pyplot as plt

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

dates = []
amount = []
ldates = []
lamount = []
records = {}

cursor.execute("""SELECT sday, day, high, low from alldata_ia 
 WHERE station = 'IA8706' and sday != '0229' ORDER by day ASC""")

for row in cursor:
    if not records.has_key(row[0]):
        records[row[0]] = {'high': -99, 'low': 99}
    if row[2] > records[row[0]]['high']:
        dates.append( row[1] )
        amount.append( row[2] - records[row[0]]['high'] )
        records[row[0]]['high'] = row[2]
    if row[3] < records[row[0]]['low']:
        ldates.append( row[1] )
        lamount.append( row[3] - records[row[0]]['low']  )
        records[row[0]]['low'] = row[3]


(fig, ax) = plt.subplots(1,1)

ax.scatter(dates, amount, color='r', label='High Temp Beat')
ax.scatter(ldates, lamount, color='b', label='Low Temp Beat')
for d,h in zip(dates, amount):
    if d.year > 1913 and h > 17:
        ax.text(d, h, d.strftime("%-d %b %Y"), va='bottom')
for d,h in zip(ldates, lamount):
    if d.year > 1913 and h < -17:
        ax.text(d, h, d.strftime("%-d %b %Y"), va='bottom')
    if d.year == 2014 and h < -10:
        ax.text(d, h+0.5, d.strftime("%-d %b %Y"), ha='right')
    elif d.year > 1990 and h < -11:
        ax.text(d, h-0.5, d.strftime("%-d %b %Y"), va='top')
ax.grid(True)
ax.set_ylabel("Daily Record Temperature Beat $^\circ$F")
ax.set_title("1893-3 March 2014 Waterloo Daily Record Temp Beat Margin")
ax.set_ylim(-30,30)
ax.legend(ncol=2, fontsize=12)

fig.savefig("test.png")
