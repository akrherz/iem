import psycopg2
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

obvalid = []
obtmpf = []
obroad = []
obdwpf = []
icursor.execute("""SELECT valid, tmpf, dwpf, tsf0 from current_log c JOIN stations s ON
 (s.iemid = c.iemid) WHERE c.valid > '2015-01-20 05:00' and 
 c.valid < '2015-01-20 10:00' 
 and s.id = 'RJFI4' ORDER by valid
 ASC""")
for row in icursor:
    obvalid.append( row[0])
    obtmpf.append( row[1])
    obdwpf.append(row[2])
    obroad.append( row[3] )

#obvalid2 = []
#obwx = []
#icursor.execute("""SELECT valid, presentwx from current_log c JOIN stations s ON
# (s.iemid = c.iemid) WHERE c.valid > '2014-01-16' and c.valid < '2014-01-16 17:30' 
# and s.id = 'DSM' and presentwx is not null ORDER by valid
# ASC""")
#for row in icursor:
#    obvalid2.append( row[0])
#    obwx.append( row[1].replace(",FG", "").replace(",FZFG", ""))

def get_roads(segid):
    pcursor.execute("""SELECT valid, cond_code from roads_2015_log where
      segid = %s and valid > '2015-01-20' ORDER by valid ASC""", (segid,))

    valid = []
    codes = []
    oldcode = -1
    for row in pcursor:
        if row[1] != oldcode:
            valid.append( row[0] )
            codes.append( row[1] )
        oldcode = row[1]

    valid.append( row[0] )
    codes.append( row[1] )
    return valid, codes

valid, codes = get_roads(2428)

def get_color(code):
    if code == 0:
        return 'w'
    if code == 1:
        return 'g'
    if code in [27,15,31,39,3]:
        return 'yellow'
    if code in [35,27,47,11]:
        return 'r'
    return 'k'
        

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1, sharex=True)

for i in range(1,len(valid)):
    print valid[i-1], valid[i], codes[i-1]
    rect = plt.Rectangle((valid[i-1],24), 
                         (valid[i]-valid[i-1]).seconds / (24.0 *1440.0), 1.5,
                         fc=get_color(codes[i-1]), zorder=1, ec='None')
    ax.add_patch(rect)
    
ax.plot(obvalid, obtmpf, lw=2, zorder=2, color='b', label='Air Temp')
ax.plot(obvalid, obdwpf, lw=2, zorder=2, color='g', label='Dew Point')
ax.plot(obvalid, obroad, lw=2, zorder=2, color='r', label='Road Temp')
l = ""
#for v, t in zip(obvalid2, obwx):
#    if t != l:
#        l = t
#        ax.text(v, 39.85, t, rotation=90, va='top', ha='center')
ax.grid(True)
ax.set_title("20 Jan 2015 Jefferson RWIS Temps\nDOT/State Patrol Road Condition for US30 near Jefferson")

import pytz, datetime
now = datetime.datetime(2015,1,20,0,0)
now = now.replace(tzinfo=pytz.timezone("America/Chicago"))
ets = datetime.datetime(2015,1,21,0,0)
ets = ets.replace(tzinfo=pytz.timezone("America/Chicago"))
interval = datetime.timedelta(seconds=3600)
xticks = []
xticklabels = []
while now < ets:
    xticks.append( now )
    xticklabels.append( now.strftime("%-I %p"))
    now += interval
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlim(min(obvalid), max(obvalid))
#ax.set_ylim(24,36)
ax.set_ylim(22, 36)
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax.set_xlabel("Morning of 20 January 2015")
ax.text( obvalid[-17], 22.7, "Completely Covered\nFrost", ha='center', color='r')
ax.text( obvalid[-12], 26, "Partially Covered\nFrost", ha='center', color='y')
#ax.text( obvalid[0], 29.75, "Wet", color='g')
ax.axhline(32, color='tan', lw=2)
ax.axvline(obvalid[-8], color='tan', lw=2)
ax.legend(loc=2)
ax.grid(True)

fig.savefig('test.png')
