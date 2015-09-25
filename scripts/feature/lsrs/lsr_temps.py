import iemdb
import datetime
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

pcursor.execute("""SELECT distinct ST_X(geom), ST_Y(geom), magnitude, valid , wfo,
  state from lsrs_2013 WHERE valid > '2013-04-09 00:00' 
  and valid < '2013-04-11 00:00' and typetext = 'HAIL'
  and state in ('IA','WI','MN','NE','SD','KS')
  ORDER by valid ASC""")

sizes = []
temps = []
sizes2 = []
temps2 = []

for row in pcursor:
    lon = row[0]
    lat = row[1]
    icursor.execute("""SELECT ST_DISTANCE(geom, 
    ST_SetSrid(ST_GeomFromText('POINT(%s %s)'),4326)) as dist, id, network
    from stations WHERE country = 'US' and (network ~* 'AWOS' or network ~* 'ASOS')
    and ST_X(geom) BETWEEN %s and %s and 
    ST_Y(geom) BETWEEN %s and %s ORDER by dist ASC LIMIT 5""" % (lon, lat,
                    lon - 0.5, lon + 0.5, lat - 0.5, lat + 0.5))
    stids = []
    for row2 in icursor:
        if row[0] < 0.5:
            stids.append( row2[1] )
    if len(stids) == 0:
        continue
    
    tmpf = None
    for stid in stids:
        icursor.execute("""SELECT tmpf from current_log c JOIn stations s on
        (s.iemid = c.iemid) WHERE s.id = '%s' and c.valid BETWEEN '%s' and '%s'
        """ % (stid, row[3] - datetime.timedelta(minutes=15), 
               row[3] + datetime.timedelta(minutes=15)))
        row2 = icursor.fetchone()
        if row2 is None:
            continue
        tmpf = row2[0]
        break
    
    if tmpf is None:
        continue
    
    print tmpf, row[2], row[4]
    if row[5] == 'IA':
        sizes2.append( row[2])
        temps2.append( tmpf )
    else:
        sizes.append( row[2])
        temps.append( tmpf )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.scatter(temps, sizes, marker='.', color='b', s=70, zorder=2)
ax.scatter(temps2, sizes2, marker='x', color='r', s=70, zorder=3, label='Iowa Reports')
ax.plot([32,32],[0,3], linestyle='--', color='k')
ax.text(32.4,2.8, "32$^{\circ}\mathrm{F}$")
ax.grid(True)
ax.set_title("9-10 Apr 2013 NWS Hail Reports + Surface Air Temps\nFor Iowa, Wisconsin, Minnesota, Nebraska, South Dakota, Kansas")
ax.set_ylabel("Reported Hail Size [inch]")
ax.set_xlabel("Surface Air Temperature $^{\circ}\mathrm{F}$\nwithin ~40 miles and 30 minutes of report")
ax.set_ylim(0,3)
ax.legend(loc='best')
fig.savefig('test.png')
