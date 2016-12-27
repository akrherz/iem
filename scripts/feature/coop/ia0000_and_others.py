import psycopg2
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt

IEM = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = IEM.cursor()


def get(month):
    cursor.execute("""
     select day, sum(case when precip > 0 then 1 else 0 end), count(*),
     max(case when station = 'IA0000' then precip else 0 end) from
     alldata_ia where station in (SELECT distinct station from alldata_ia
     where year = 1951 and precip > 0)
     and year > 1950  and month = %s GROUP by day
    """, (month,))

    ratio = []
    precip = []
    for row in cursor:
        if row[3] < 0.02 or row[3] > 1.0:
            continue
        ratio.append(row[1] / float(row[2]) * 100.0)
        precip.append(row[3])

    H, xedges, yedges = np.histogram2d(ratio, precip, bins=(30, 30),
                                       range=[[0, 100], [0, 1.0]])
    H2 = ma.array(H)
    H2.mask = np.where(H < 0.001, True, False)
    extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
    return H2, extent

(fig, ax) = plt.subplots(2, 2, sharex=True, sharey=True)
fig.text(0.5, 0.95, "Iowa Daily Precipitation Coverage vs Areal Average Total",
         ha='center')

H2, extent = get(1)
ax[0, 0].imshow(H2, interpolation='nearest', extent=extent, aspect='auto')
ax[0, 0].set_ylim(0, 100)
ax[0, 0].grid(True)
ax[0, 0].text(0.8, 20, "January", ha='center')
ax[0, 0].set_ylabel("Areal Coverage [%]")

H2, extent = get(4)
ax[0, 1].imshow(H2, interpolation='nearest', extent=extent, aspect='auto')
ax[0, 1].grid(True)
ax[0, 1].text(0.8, 20, "April", ha='center')

H2, extent = get(7)
ax[1, 0].imshow(H2, interpolation='nearest', extent=extent, aspect='auto')
ax[1, 0].grid(True)
ax[1, 0].text(0.8, 20, "July", ha='center')
ax[1, 0].set_ylabel("Areal Coverage [%]")
ax[1, 0].set_xlabel("Precipitation [inch]")

H2, extent = get(10)
ax[1, 1].imshow(H2, interpolation='nearest', extent=extent, aspect='auto')
ax[1, 1].grid(True)
ax[1, 1].text(0.8, 20, "October", ha='center')
ax[1, 1].set_xlabel("Precipitation [inch]")

fig.savefig('test.png')
