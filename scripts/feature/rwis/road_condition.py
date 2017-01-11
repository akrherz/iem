import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg2
import datetime
from pandas.io.sql import read_sql
import pytz
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

obsdf = read_sql("""
    SELECT valid, tmpf, dwpf, tsf0, tsf1 from current_log c JOIN stations s ON
    (s.iemid = c.iemid) WHERE c.valid > '2017-01-10 03:00' and
    c.valid < '2017-01-10 15:00'
    and s.id = 'RJFI4' ORDER by valid ASC
    """, IEM, index_col='valid')

raddf = read_sql("""
    SELECT valid, srad from current_log c JOIN stations s ON
    (s.iemid = c.iemid) WHERE c.valid > '2017-01-10 08:00' and
    c.valid < '2017-01-10 15:00'
    and s.id = 'SJEI4' ORDER by valid ASC
    """, IEM, index_col='valid')


def get_roads(segid):
    pcursor.execute("""
        SELECT valid, cond_code from roads_2015_2016_log where
        segid = %s and valid > '2017-01-10' ORDER by valid ASC
    """, (segid,))

    valid = []
    codes = []
    oldcode = -1
    for row in pcursor:
        if row[1] != oldcode:
            valid.append(row[0])
            codes.append(row[1])
        oldcode = row[1]

    if row[1] != 0:
        valid.append(row[0] + datetime.timedelta(days=1))
        codes.append(0)
    return valid, codes

valid, codes = get_roads(5575)


def get_color(code):
    if code == 0:
        return 'w'
    if code == 1:
        return 'g'
    if code in [27, 15, 31, 39, 3]:
        return 'yellow'
    if code in [35, 27, 47, 11]:
        return 'r'
    return 'k'


(fig, ax) = plt.subplots(1, 1, sharex=True)
ax.plot(obsdf.index.values, obsdf['tmpf'], lw=2, zorder=3, color='r',
        label='Air Temp')
ax.plot(obsdf.index.values, obsdf['dwpf'], lw=2, zorder=3, color='g',
        label='Dew Point')
ax.plot(obsdf.index.values, obsdf['tsf0'], lw=2, zorder=3, color='b',
        label='Road Temp')
ax.plot(obsdf.index.values, obsdf['tsf1'], lw=2, zorder=3, color='pink',
        label='Bridge Temp')

ax2 = ax.twinx()
ax2.plot(raddf.index.values, raddf['srad'], lw=2, zorder=2, color='k')
ax2.set_ylabel("Solar Radiation [W m$^{-2}$] (black line)")
ax2.set_ylim(0, 1000)

ax.set_zorder(ax2.get_zorder()+1)
ax.patch.set_visible(False)
for i in range(1, len(valid)):
    days = (valid[i]-valid[i-1]).total_seconds() / 86400.
    rect = plt.Rectangle((mdates.date2num(valid[i-1]), 35),
                         days, 1.5,
                         fc=get_color(codes[i-1]), zorder=1, ec='None')
    ax.add_patch(rect)
    print valid[i-1] + datetime.timedelta(seconds=((days / 2.) * 86400.))
    ax.text(valid[i-1] + datetime.timedelta(seconds=((days / 2.) * 86400.)),
            35.5, "Partially Ice Covered", ha='center', va='center')

l = ""
ax.grid(True)
ax.set_title(("10 Jan 2017 Jefferson RWIS Temps + SchoolNet Radiation\n"
              "DOT/State Patrol Road Condition for US-30 near Jefferson"))

ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I %p",
                             tz=pytz.timezone("America/Chicago")))
# ax.set_ylim(24,36)
ax.set_ylim(22, 36)
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax.set_xlabel("10 January 2017 - Central Standard Time")
ax.axhline(32, color='tan', lw=2)
ax.legend(loc=(0.3, 0.2), fontsize=12)
ax.grid(True)

fig.savefig('test.png')
