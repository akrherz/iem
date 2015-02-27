"""
Plot a comparison of NARR solar rad vs ISUAG
"""
import psycopg2
import numpy
import datetime
import matplotlib.pyplot as plt
from scipy import stats
ISUAG = psycopg2.connect(databse='isuag', host='iemdb')
icursor = ISUAG.cursor()
COOP = psycopg2.connect(database='coop', host='iemdb')
ccursor = COOP.cursor()
from pyiem.network import Table as NetworkTable
nt = NetworkTable("ISUAG")


def do(station):
    csite = nt.sts[station]['climate_site']
    data = {}
    icursor.execute("""SELECT valid, c80 from daily where c80 > 0
     and station = %s""", (station,))
    for row in icursor:
        data[row[0]] = float(row[1])

    obs = []
    model = []
    minvalid = datetime.date(2013, 3, 1)
    maxvalid = datetime.date(1980, 1, 1)
    ccursor.execute("""SELECT day, merra_srad from alldata_ia where merra_srad > 0
      and station = %s """, (csite,))
    for row in ccursor:
        if row[0] in data:
            obs.append(data[row[0]])
            model.append(float(row[1]))
            if row[0] < minvalid:
                minvalid = row[0]
            if row[0] > maxvalid:
                maxvalid = row[0]

    if len(obs) < 10:
        return
    obs = numpy.array(obs)
    model = numpy.array(model)

    (fig, ax) = plt.subplots(1, 1)
    bias = numpy.average((model - obs))
    h_slope, intercept, h_r_value, _, _ = stats.linregress(model, obs)
    ax.scatter(model, obs, color='tan', edgecolor='None')
    ax.set_xlabel("MERRA Grid Extracted (langleys)")
    ax.set_ylabel("ISUAG Observation (langleys)")
    ax.set_title(("%s Daily Solar Radiation Comparison (%s-%s)"
                  ) % (nt.sts[station]['name'],
                       minvalid.strftime("%-d %b %Y"),
                       maxvalid.strftime("%-d %b %Y")))
    ax.plot([0, 800], [0, 800], lw=3, color='r', zorder=2, label='1to1')
    ax.plot([0, 800], [0-bias, 800-bias], lw=3, color='k', zorder=2,
            label='model bias = %.1f' % (bias,))
    ax.plot([0, 800], [intercept, intercept + 800.0 * h_slope], color='g',
            lw=3, zorder=2, label=r"Fit: $R^2 = %.2f$" % (h_r_value ** 2,))
    ax.legend(loc=2)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    fig.savefig('%s.png' % (nt.sts[station]['name'].replace(" ", "_"),))
    del fig
    print '%-20s %.1f %.2f' % (nt.sts[station]['name'], bias, h_r_value ** 2)

for sid in nt.sts.keys():
    do(sid)
