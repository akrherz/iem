"""Generates the nice histograms on the IEM website"""
from __future__ import print_function
import datetime
import calendar
import os

import pytz
import numpy as np
import matplotlib.pyplot as plt
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, utc
from pyiem.plot import maue

cmap = maue()
cmap.set_bad('white')
cmap.set_under('white')
cmap.set_over('black')

today = datetime.datetime.now()
today = today.replace(tzinfo=pytz.utc)

POSTGIS = get_dbconn('radar', user='nobody')


def run(nexrad):
    drct = []
    sknt = []
    doy = []
    minvalid = utc(2016, 1, 1)
    cursor = POSTGIS.cursor()
    cursor.execute("""
    SELECT drct, sknt, extract(doy from valid), valid
    from nexrad_attributes_log WHERE nexrad = %s and sknt > 0
    """, (nexrad,))
    for row in cursor:
        drct.append(row[0])
        sknt.append(row[1])
        doy.append(row[2])
        if row[3] < minvalid:
            minvalid = row[3]
    cursor.close()
    print("  RADAR: %s found %s entries since %s" % (nexrad, len(doy),
                                                     minvalid))

    years = (today - minvalid).days / 365.25
    (fig, ax) = plt.subplots(2, 1, figsize=(9, 7), dpi=100)

    H2, xedges, yedges = np.histogram2d(drct, sknt, bins=(36, 15),
                                        range=[[0, 360], [0, 70]])
    H2 = np.ma.array(H2 / years)
    H2.mask = np.where(H2 < 1, True, False)
    res = ax[0].pcolormesh(xedges, yedges, H2.transpose(), cmap=cmap)
    fig.colorbar(res, ax=ax[0], extend='both')
    ax[0].set_xlim(0, 360)
    ax[0].set_ylabel("Storm Speed [kts]")
    ax[0].set_xticks((0, 90, 180, 270, 360))
    ax[0].set_xticklabels(('N', 'E', 'S', 'W', 'N'))
    ax[0].set_title(("%s - %s K%s NEXRAD Storm Attributes Histogram\n"
                     "%s total attrs, units are ~ (attrs+scans)/year"
                     ) % (minvalid.strftime("%d %b %Y"),
                          today.strftime("%d %b %Y"), nexrad, len(drct),))
    ax[0].grid(True)

    H2, xedges, yedges = np.histogram2d(doy, drct, bins=(36, 36),
                                        range=[[0, 365], [0, 360]])
    H2 = np.ma.array(H2 / years)
    H2.mask = np.where(H2 < 1, True, False)
    res = ax[1].pcolormesh(xedges, yedges, H2.transpose(), cmap=cmap)
    fig.colorbar(res, ax=ax[1], extend='both')
    ax[1].set_ylim(0, 360)
    ax[1].set_ylabel("Movement Direction")
    ax[1].set_yticks((0, 90, 180, 270, 360))
    ax[1].set_yticklabels(('N', 'E', 'S', 'W', 'N'))
    ax[1].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305,
                      335, 365))
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].set_xlim(0, 365)
    ax[1].grid(True)

    ax[1].set_xlabel(("Generated %s by Iowa Environmental Mesonet"
                      ) % (today.strftime("%d %b %Y"),))

    fig.savefig('%s_histogram.png' % (nexrad,))
    plt.close()


def main():
    """ See how we are called """
    nt = NetworkTable(["NEXRAD", "TWDR"])
    for sid in nt.sts:
        if os.path.isfile("%s_histogram.png" % (sid,)):
            print("  Skipping %s" % (sid,))
            continue
        run(sid)


if __name__ == '__main__':
    main()
