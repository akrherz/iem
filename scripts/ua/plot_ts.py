import matplotlib.pyplot as plt
import psycopg2
import matplotlib.dates as mdates

dbconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = dbconn.cursor()

times = []
h = []
s = []
cursor.execute("""
 select valid, height, smps from raob_profile_2013 p JOIN raob_flights f on 
 (p.fid = f.fid) where f.station = 'KOAX'  and 
 p.pressure = 500 and p.height < 7000 ORDER by valid ASC
""")
for row in cursor:
    h.append( row[1] )
    times.append( row[0] )
    s.append( row[2] )
    
(fig, ax) = plt.subplots(1,1)

ax.plot(times, h)
ax2 = ax.twinx()
ax2.plot(times, s, color='r')
ax2.set_ylabel("Wind Speed [$m s^{-1}$]")
ax.grid(True)
ax.set_title("Omaha RAOB 500 hPa Height")
ax.set_ylabel("Height above sea level [m]")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y'))


fig.savefig('test.png')