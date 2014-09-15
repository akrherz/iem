import psycopg2
import pytz
import matplotlib.dates as mdates
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()

cursor.execute("""
 select valid, pday, lag(pday) over (order by valid ASC) 
 from current_log where iemid = 1238 and 
 valid > '2013-07-21 12:20' and valid < '2013-07-21 14:00' ORDER by valid ASC
""")

valid = [0]*60
pday = [0]*60
rate1 = [0]*60
rate15 = [0]*60
rate60 = [0]*60
for row in cursor:
    if row[2] is None:
        continue
    valid.append( row[0] )
    pday.append( row[1])
    rate1.append( (row[1]-row[2]) * 60.0 )
    rate15.append( (row[1]-pday[-14]) * 4.0 )
    rate60.append( (row[1]-pday[-59])  )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)
ax.bar(valid[60:], rate1[60:], width=(1./1440.), label='Hourly Rate over 1 min',
       fc='tan', ec='tan')
ax.plot(valid[60:], pday[60:], lw=2, label='Total Precip')
ax.plot(valid[60:], rate15[60:], lw=2, label='Hourly Rate over 15 min')
ax.plot(valid[60:], rate60[60:],lw=2, label='Actual Hourly Rate')
ax.grid(True)
ax.legend(loc=2,ncol=1)
ax.set_ylabel("Precipitation [inch]")
ax.set_xlabel("21 July 2013 :: 12:30 to 2:00 PM")
ax.set_title("Chariton KCCI-TV SchoolNet Precipitation (3.56\") ")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-I:%M',
                             tz=pytz.timezone('America/Chicago')))


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')