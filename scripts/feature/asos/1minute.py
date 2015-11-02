import psycopg2
import datetime
import pytz
from pyiem.network import Table as NetworkTable
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

nt = NetworkTable("IA_ASOS")

ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = ASOS.cursor()


def get_data(station):
    cursor.execute("""SELECT valid, tmpf from t2015_1minute
    where station = %s and valid > '2015-02-05' and tmpf is not null
    ORDER by valid ASC
    """, (station, ))
    valid = []
    tmpf = []
    for row in cursor:
        valid.append(row[0])
        tmpf.append(row[1])
    return valid, tmpf

(fig, ax) = plt.subplots(1, 1)

for sid in ['DSM', 'ALO', 'AMW', 'MCW', 'MIW']:
    d, t = get_data(sid)
    ax.plot(d, t, label="%s %s$^\circ$F" % (nt.sts[sid]['name'], min(t)),
            lw=2.)

ax.legend(loc=2)
ax.grid(True)

ax.set_title("5 February 2015 Morning Temperature Timeseries")
ax.set_ylabel("Temperature $^\circ$F")

tz = pytz.timezone("America/Chicago")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-I %p', tz=tz))

ax.set_xlim(datetime.datetime(2015, 2, 5, 10),
            datetime.datetime(2015, 2, 5, 16))
ax.set_xlabel("CST, One Minute Iowa ASOS Data Provided by NCDC")
fig.savefig('test.png')
