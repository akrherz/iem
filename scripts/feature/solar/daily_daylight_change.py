import ephem
import datetime
from pyiem.network import Table as NetworkTable
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

sun = ephem.Sun()
nt = NetworkTable(("IA_ASOS", "AK_ASOS", "MI_ASOS", "FL_ASOS"))


def do(lon, lat):
    ''' Compute the daily daylight change '''
    loc = ephem.Observer()
    loc.lat = str(lat)
    loc.long = str(lon)

    delta = []
    days = []
    sts = datetime.datetime(2004, 1, 1)
    ets = datetime.datetime(2005, 1, 2)
    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        loc.date = now.strftime("%Y/%m/%d 10:00")
        rise1 = loc.next_rising(sun).datetime()
        set1 = loc.next_setting(sun).datetime()
        day1 = (set1 - rise1).seconds + (set1 - rise1).microseconds / 1000000.0
        delta.append(day1)
        now += interval
        days.append(now)
    return days, np.array(delta)

days, dsmdelta = do(nt.sts['DSM']['lon'], nt.sts['DSM']['lat'])
days, pancdelta = do(nt.sts['PANC']['lon'], nt.sts['PANC']['lat'])
days, miadelta = do(nt.sts['MIA']['lon'], nt.sts['MIA']['lat'])

(fig, ax) = plt.subplots(2, 1, sharex=True)

ax[0].plot(days, dsmdelta, label='Des Moines')
ax[0].plot(days, miadelta, label='Miami')
ax[0].plot(days, pancdelta, label='Anchorage')
ax[0].grid(True)
ax[0].set_ylabel("Daylight Hours")
ax[0].set_yticks(np.arange(6, 21, 2)*3600.0)
ax[0].set_yticklabels(np.arange(6, 21, 2))
ax[0].set_ylim(5*3600.0, 19.5*3600.)
ax[0].xaxis.set_major_locator(
                               mdates.MonthLocator(interval=1)
                               )
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax[0].legend(loc=1, fontsize=10)
ax[0].set_title("Daylight Time")


ax[1].plot(days[:-1], dsmdelta[1:] - dsmdelta[:-1])
ax[1].plot(days[:-1], miadelta[1:] - miadelta[:-1])
ax[1].plot(days[:-1], pancdelta[1:] - pancdelta[:-1])
ax[1].grid(True)
ax[1].set_yticks(range(-360, 361, 60))
ax[1].set_yticklabels(range(-6, 7, 1))
ax[1].set_ylabel("Daily Daylight Change [minutes]", fontsize=10)

fig.savefig('test.png')
