import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

def get(station):
    ccursor.execute("""SELECT day, o.precip as ob_precip, c.precip as c_precip
  from alldata_ia o JOIN climate c on (c.station = o.station and
  o.sday = to_char(c.valid, 'mmdd')) WHERE o.station = %s and
  o.day > '2011-01-01' ORDER by day DESC""", (station,))

    days = []
    diff = []
    running = 0
    for row in ccursor:
        running += (row[1] - row[2])
        days.append( row[0] )
        diff.append( running )

    return days, diff

days1, diff1 = get("IA0000")
days2, diff2 = get("IA0200")
days3, diff3 = get("IA7708")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(1,1)

ax.plot(days1, diff1, lw=2, label="Iowa")
ax.plot(days2, diff2, lw=2, label="Ames")
ax.plot(days3, diff3, lw=2, label="Sioux City")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.grid(True)
ax.legend(loc='best')
ax.set_title("Precipitation Departure from date to 15 April 2013")
ax.set_ylabel("Precipitation Departure [inch]")
ax.set_xlabel("From Date to 15 April 2013")


fig.savefig('test.png')
