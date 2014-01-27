import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

obvalid = []
obtmpf = []
obroad = []
icursor.execute("""SELECT valid, tmpf, tsf0 from current_log c JOIN stations s ON
 (s.iemid = c.iemid) WHERE c.valid > '2014-01-16 14:00' and 
 c.valid < '2014-01-16 18:00' 
 and s.id = 'RTOI4' ORDER by valid
 ASC""")
for row in icursor:
    obvalid.append( row[0])
    obtmpf.append( row[1])
    obroad.append( row[2] )

obvalid2 = []
obwx = []
icursor.execute("""SELECT valid, presentwx from current_log c JOIN stations s ON
 (s.iemid = c.iemid) WHERE c.valid > '2014-01-16' and c.valid < '2014-01-16 17:30' 
 and s.id = 'DSM' and presentwx is not null ORDER by valid
 ASC""")
for row in icursor:
    obvalid2.append( row[0])
    obwx.append( row[1].replace(",FG", "").replace(",FZFG", ""))

def get_roads(segid):
    pcursor.execute("""SELECT valid, cond_code from roads_2014_log where
      segid = %s and valid > '2014-01-16' ORDER by valid ASC""", (segid,))

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

valid, codes = get_roads(2558)

def get_color(code):
    if code == 0:
        return 'w'
    if code == 1:
        return 'g'
    if code in [27,15,31,39]:
        return 'yellow'
    if code in [35,27,47]:
        return 'r'
    return 'k'
        

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1, sharex=True)

for i in range(1,len(valid)):
    print valid[i-1], valid[i], codes[i-1]
    rect = plt.Rectangle((valid[i-1],25), 
                         (valid[i]-valid[i-1]).seconds / (24.0 *1440.0), 2,
                         fc=get_color(codes[i-1]), zorder=1, ec='None')
    ax.add_patch(rect)
    
ax.plot(obvalid, obtmpf, lw=2, zorder=2, color='b', label='Air Temp')
ax.plot(obvalid, obroad, lw=2, zorder=2, color='g', label='Road Temp')
l = ""
for v, t in zip(obvalid2, obwx):
    if t != l:
        l = t
        ax.text(v, 39.85, t, rotation=90, va='top', ha='center')
ax.grid(True)
ax.set_title("16 Jan 2014 Altoona (Des Moines) RWIS Temps\nDes Moines Airport Present Wx + DOT Road Condition")

import pytz, datetime
now = datetime.datetime(2014,1,16,0,0)
now = now.replace(tzinfo=pytz.timezone("America/Chicago"))
ets = datetime.datetime(2014,1,17,0,0)
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
ax.set_ylim(top=41)
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")

ax.text( obvalid[-8], 23.75, "Completely Covered", color='r')
ax.text( obvalid[-12], 27.25, "Partially Covered", color='y')
#ax.text( obvalid[0], 29.75, "Wet", color='g')
ax.axhline(32, color='tan', lw=2)
ax.legend(loc=3)
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')