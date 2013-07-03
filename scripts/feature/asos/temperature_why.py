import psycopg2
"""
ASOS = psycopg2.connect(database='asos', user='nobody', host='iemdb')
cursor = ASOS.cursor()

cursor.execute(""
select date(valid) as d, sum(p01i) from alldata where extract(month from valid) = 7 and extract(hour from valid) between 8 and 16 and extract(day from valid) < 8 and station = 'DSM' and p01i > 0 GROUP by d
"")
rains = {}
for row in cursor:
  rains[ row[0].strftime("%Y%m%d") ] = True

avgt = 83.6

cursor.execute(""
select valid, tmpf, case when skyc1 = 'OVC' or skyc2 = 'OVC' or skyc3 = 'OVC' or skyc4 = 'OVC' then 1 else 0 end from alldata where station = 'DSM' and extract(month from valid) = 7 and extract(hour from valid + '10 minute'::interval) = 16 and extract(day from valid) < 8 and extract(minute from valid) in (54,0) 

  and valid > '1951-01-01' ORDER by tmpf DESC
"")
#    Temp
#    A B
# T
# F
clouds = [[0,0], [0,0]]
precip = [[0,0], [0,0]]
for row in cursor:
    above = 0
    if row[1] < avgt:
        above = 1

    c = 1
    if row[2] == 1:
        c = 0

    p = 0
    if rains.get( row[0].strftime("%Y%m%d"), 0) > 0:
        p = 1
    clouds[above][c] += 1.0
    precip[above][p] += 1.0
"""
#print clouds
#print precip
#          ABOVE          BELOW
clouds = [[21.0, 199.0], [67.0, 146.0]]
precip = [[205.0, 15.0], [169.0, 44.0]]
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2,2)

# Did it rain
nr_ab = precip[0][0]
r_ab = precip[0][1]
nr_be = precip[1][0]
r_be = precip[1][1]
ovc_ab = clouds[0][0]
noc_ab = clouds[0][1]
ovc_be = clouds[1][0]
noc_be = clouds[1][1]

fig.text(0.5, 0.1, "1-7 July 1951-2012 Des Moines 4 PM Temperature", ha='center', bbox=dict(boxstyle='round', facecolor='#FFFFFF'))
fig.text(0.5, 0.43, r"Above 83.6$^\circ$F", ha='center', bbox=dict(boxstyle='round', facecolor='pink'))
fig.text(0.5, 0.38, r"Below 83.6$^\circ$F", ha='center', bbox=dict(boxstyle='round', facecolor='lightblue'))
fig.text(0.5, 0.86, r"Above 83.6$^\circ$F", ha='center', bbox=dict(boxstyle='round', facecolor='pink'))
fig.text(0.5, 0.81, r"Below 83.6$^\circ$F", ha='center', bbox=dict(boxstyle='round', facecolor='lightblue'))

ax[0,0].pie([nr_ab,nr_be],  colors=['pink','lightblue'],
    autopct='%1.1f%%')
ax[0,0].set_title("No Rain between 8 AM - 4 PM")
ax[1,0].pie([r_ab,r_be],  colors=['pink','lightblue'],
    autopct='%1.1f%%')
ax[1,0].set_title("Rained between 8 AM - 4 PM")
ax[0,1].pie([ovc_ab, ovc_be],  colors=['pink','lightblue'],
    autopct='%1.1f%%')
ax[0,1].set_title("Sky is Overcast @4PM")
ax[1,1].pie([noc_ab,noc_be],  colors=['pink','lightblue'],
    autopct='%1.1f%%')
ax[1,1].set_title("Sky is not Overcast @4PM")

fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')
