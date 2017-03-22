import matplotlib.pyplot as plt
import matplotlib.font_manager
import numpy
import psycopg2
pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = pgconn.cursor()
prop = matplotlib.font_manager.FontProperties(size=10)

(fig, axes) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
ax = axes[0]
ax.set_xlim(0, 1443)
xticks = []
xticklabels = []
for x in range(0, 25, 2):
    xticks.append(x * 60)
    if x == 0 or x == 24:
        lbl = 'Mid'
    elif x == 12:
        lbl = 'Noon'
    else:
        lbl = x % 12
    xticklabels.append(lbl)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
# ax.set_xlabel("Local Hour of Day [CDT]")
# ax.set_ylabel("Air & Dew Point (dash) Temp [F]", fontsize=9)
ax.set_title("21 March 2017 Temperature Time Series\nAububon and Des Moines Experienced Snow")
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
axes[1].set_xlabel("CDT")
ax.set_ylim(15, 65)


names = {'CBF': 'Council Bluffs', 'AXA': 'Algona', 'SHL': 'Sheldon',
         'TNU': 'Newton', 'AWG': 'Washington', 'DEH': 'Decorah',
         'BNW': 'Boone', 'ADU': 'Audubon', 'AMW': 'Ames',
         'DSM': 'Des Moines', 'MIW': 'Marshalltown'}

for sid, color in zip(['ADU', 'DSM', 'MIW'], ['b', 'r', 'g']):
    cursor.execute("""
        SELECT valid, tmpf, dwpf from
        current_log c JOIN stations s on (s.iemid = c.iemid)
        where valid > '2017-03-21' and
        valid < '2017-03-22' and s.id = '%s' and tmpf > 0 ORDER by valid ASC
        """ % (sid,))
    times = []
    tmpf = []
    dwpf = []
    for row2 in cursor:
        times.append(row2[0].hour * 60 + row2[0].minute)
        tmpf.append(row2[1])
        dwpf.append(row2[2])
    tmpf = numpy.array(tmpf)
    dwpf = numpy.array(dwpf)
    ax.plot(times, tmpf, color=color, linestyle='-', label='%s Temp' % (names[sid],))
    ax.plot(times, dwpf, color=color, linestyle='-.', label='%s Dewpt' % (names[sid],))
    axes[1].plot(times, tmpf - dwpf, color=color, label='%s' % (names[sid],))
ax.grid(True)
axes[1].grid(True)
axes[1].set_ylabel("Dew Point Depression $^{\circ}\mathrm{F}$")
ax.legend(loc=2, ncol=3, prop=prop)

fig.savefig('test.png')
