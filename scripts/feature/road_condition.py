import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

obvalid = []
obtmpf = []
icursor.execute("""SELECT valid, tmpf from current_log c JOIN stations s ON
 (s.iemid = c.iemid) WHERE c.valid > '2013-01-27' and c.valid < '2013-01-28' and s.id = 'OT0002' ORDER by valid
 ASC""")
for row in icursor:
    obvalid.append( row[0])
    obtmpf.append( row[1])

obvalid2 = []
obtmpf2 = []
icursor.execute("""SELECT valid, tmpf from current_log c JOIN stations s ON
 (s.iemid = c.iemid) WHERE c.valid > '2013-01-27' and c.valid < '2013-01-28' and s.id = 'MCW' ORDER by valid
 ASC""")
for row in icursor:
    obvalid2.append( row[0])
    obtmpf2.append( row[1])

def get_roads(segid):
    pcursor.execute("""SELECT valid, cond_code from roads_2013_log where
      segid = %s and valid > '2013-01-27' ORDER by valid ASC""", (segid,))

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

valid, codes = get_roads(856)
valid2, codes2 = get_roads(701)

def get_color(code):
    if code == 0:
        return 'w'
    if code == 1:
        return 'g'
    if code in [27,15,31]:
        return 'yellow'
    if code in [35,]:
        return 'r'
    return 'k'
        

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2,1, sharex=True)

for i in range(1,len(valid)):
    print valid[i-1], valid[i], codes[i-1]
    rect = plt.Rectangle((valid[i-1],25), 
                         (valid[i]-valid[i-1]).seconds / (24.0 *1440.0), 2,
                         fc=get_color(codes[i-1]), zorder=1, ec='None')
    ax[0].add_patch(rect)
    
ax[0].plot(obvalid, obtmpf, lw=2, zorder=2)
ax[0].grid(True)
ax[0].set_title("27 Jan 2013 Road Conditions & Air Temperatures\nI-35 Road Condition near Ames")
ax[1].set_title("I-35 Road Condition near Mason City")

for i in range(1,len(valid2)):
    print valid2[i-1], valid2[i], codes2[i-1]
    rect = plt.Rectangle((valid2[i-1],25), 
                         (valid2[i]-valid2[i-1]).seconds / (24.0 *1440.0), 2,
                         fc=get_color(codes2[i-1]), zorder=1, ec='None')
    ax[1].add_patch(rect)


ax[1].plot(obvalid2, obtmpf2, lw=2, zorder=2)
ax[1].grid(True)
import pytz, datetime
now = datetime.datetime(2013,1,27,0,0)
now = now.replace(tzinfo=pytz.timezone("America/Chicago"))
ets = datetime.datetime(2013,1,28,0,0)
ets = ets.replace(tzinfo=pytz.timezone("America/Chicago"))
interval = datetime.timedelta(seconds=7200)
xticks = []
xticklabels = []
while now < ets:
    xticks.append( now )
    xticklabels.append( now.strftime("%-I %p"))
    now += interval
ax[0].set_xticks(xticks)
ax[0].set_xticklabels(xticklabels)
ax[0].set_xlim(min(obvalid), max(obvalid))
ax[0].set_ylim(24,36)
ax[0].set_ylabel("Air Temperature $^{\circ}\mathrm{F}$")
ax[1].set_ylim(24,36)
ax[1].set_ylabel("Air Temperature $^{\circ}\mathrm{F}$")

ax[1].text( obvalid2[0], 31.25, "Completely Covered", color='r')
ax[1].text( obvalid2[0], 30.5, "Partially Covered", color='y')
ax[1].text( obvalid2[0], 29.75, "Wet", color='g')

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')