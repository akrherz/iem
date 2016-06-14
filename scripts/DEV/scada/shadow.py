"""
WITH one as (SELECT id, geom from turbines),
two as (SELECT id, geom from turbines)

SELECT o.id, t.id, degrees(ST_Azimuth(o.geom, t.geom)) as az,
 ST_Distance(o.geom, t.geom) as dist from one o, two t
 WHERE o.id != t.id
"""
import psycopg2
import matplotlib.pyplot as plt
import numpy as np
pgconn = psycopg2.connect(database='scada')
cursor = pgconn.cursor()

distance = 3000
radius = 5  # half of the fan opening
turbines = 83

y = []
y2 = []
for azimuth in range(0, 360):
    a0 = azimuth - radius
    a1 = azimuth + radius
    if a0 < 0:
        a = "(azimuth > %s or azimuth < %s)" % (360 + a0, a1)
    elif a1 >= 360:
        a = "(azimuth > %s or azimuth < %s)" % (a0, a1 - 360)
    else:
        a = "azimuth between %s and %s" % (a0, a1)

    cursor.execute("""
        SELECT count(*) from shadow where """ + a + """
        and distance < %s
    """, (distance,))
    y.append(cursor.fetchone()[0])

    cursor.execute("""
        SELECT count(*) from turbines where id not in (
        SELECT distinct aid from shadow where """ + a + """
        and distance < %s)
    """, (distance,))
    y2.append(cursor.fetchone()[0] / float(turbines) * 100.)

(fig, ax) = plt.subplots(2, 1, sharex=True)
ax[0].set_title(("Number of Turbine Shadows %.0f$^\circ$ at %.3f km"
                 ) % (radius*2, distance / 1000.))
ax[0].bar(np.arange(0, 360), y, fc='blue', ec='blue')
ax[0].set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
ax[0].set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
ax[0].grid(True)
ax[0].set_xlim(0, 360)

ax[1].bar(np.arange(0, 360), y2, fc='blue', ec='blue')
ax[1].set_ylim(0, 100)
ax[1].grid(True)
ax[1].set_title("Percentage of Turbines without Shadow")

fig.savefig("test.png")
