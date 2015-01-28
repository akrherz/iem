import psycopg2
import datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = pgconn.cursor()

# Get initial
cursor.execute("""
 WITH foo as (
   SELECT ugc, generate_series(issue, init_expire, '1 minute'::interval) as t
   from warnings_2015 WHERE issue > '2015-01-25' and phenomena = 'BZ'
   and significance = 'W' and substr(ugc,1,2) != 'AK') 
   
 SELECT t at time zone 'UTC', count(*) from foo GROUP by t ORDER by t ASC""")

t1 = []
c1 = []
for row in cursor:
    t1.append(row[0].replace(tzinfo=pytz.timezone("UTC")))
    c1.append(row[1])
    
# Get initial
cursor.execute("""
 WITH foo as (
   SELECT ugc, generate_series(issue, expire, '1 minute'::interval) as t
   from warnings_2015 WHERE issue > '2015-01-25' and phenomena = 'BZ'
   and significance = 'W' and substr(ugc,1,2) != 'AK') 
   
 SELECT t at time zone 'UTC', count(*) from foo GROUP by t ORDER by t ASC""")

t2 = []
c2 = []
for row in cursor:
    t2.append(row[0].replace(tzinfo=pytz.timezone("UTC")))
    c2.append(row[1])

(fig, ax) = plt.subplots(1,1)

ax.fill_between(t1, 0, c1, zorder=1, label='Issuance', facecolor='tan',
                color='black')
ax.fill_between(t2, 0, c2, zorder=2, label='After Cancels', facecolor='blue',
                color='black')
ax.grid(True)
ax.legend(loc=2)

p1 = plt.Rectangle((0, 0), 1, 1, fc="tan")
p3 = plt.Rectangle((0, 0), 1, 1, fc="blue")
ax.legend([p1,p3], ["Issuance", "Final"], ncol=1, loc=2)

ax.set_ylabel("Number of Forecast Zones Included")
ax.set_xlabel("January 26-28 2015 Timestamps in EST\n(tan area represents zones getting removed from blizzard warning)")
ax.set_title("#Blizzardof2015 NWS Blizzard Warnings\nUGC Forecast Zones Included (ALY,BOX,CAR,GYX,OKX,PHI)")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%-I %p', 
                            tz=pytz.timezone("America/New_York")))
ax.set_xlim(min(t1)-datetime.timedelta(hours=3), max(t1)+datetime.timedelta(hours=3))
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

fig.savefig('test.png')
