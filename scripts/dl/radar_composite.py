"""Cache NEXRAD composites for the website."""
import os
import subprocess
import sys

import requests
from pyiem.util import get_dbconn, exponential_backoff, utc


TMPFN = '/tmp/radar_composite_tmp.png'
N0QBASE = utc(2010, 11, 14)


def save(sectorName, file_name, dir_name, ts, bbox=None, routes='ac'):
    ''' Get an image and write it back to LDM for archiving '''
    tstamp = ts.strftime("%Y%m%d%H%M")
    nexrad = "nexrad" if ts < N0QBASE else "n0q"
    layers = ("layers[]=%s&layers[]=watch_by_county&layers[]=sbw&"
              "layers[]=uscounties") % (nexrad, )
    if sectorName == 'conus':
        layers = (
            "layers[]=%s&layers[]=watch_by_county&layers[]=uscounties"
        ) % (nexrad, )
    uri = ("http://iem.local/GIS/radmap.php?sector=%s&ts=%s&%s"
           ) % (sectorName, tstamp, layers)
    if bbox is not None:
        uri = ("http://iem.local/GIS/radmap.php?bbox=%s&ts=%s&%s"
               ) % (bbox, tstamp, layers)
    req = exponential_backoff(requests.get, uri, timeout=60)
    if req is None or req.status_code != 200:
        print("radar_composite %s returned %s" % (uri, req.status_code))
        return

    fh = open(TMPFN, 'wb')
    fh.write(req.content)
    fh.close()

    cmd = ("/home/ldm/bin/pqinsert -p 'plot %s %s %s %s/n0r_%s_%s.png "
           "png' %s") % (routes, tstamp, file_name, dir_name, tstamp[:8],
                         tstamp[8:], TMPFN)
    subprocess.call(cmd, shell=True)

    os.unlink(TMPFN)


def runtime(ts):
    ''' Actually run for a time '''
    pgconn = get_dbconn('postgis', user='nobody')
    pcursor = pgconn.cursor()

    save('conus', 'uscomp.png', 'usrad', ts)
    save('iem', 'mwcomp.png', 'comprad', ts)
    for i in ['lot', 'ict', 'sd', 'hun']:
        save(i, '%scomp.png' % (i,), '%srad' % (i,), ts)

    # Now, we query for watches.
    pcursor.execute("""
        select sel, ST_xmax(geom), ST_xmin(geom),
        ST_ymax(geom), ST_ymin(geom) from watches_current
        ORDER by issued DESC
    """)
    for row in pcursor:
        xmin = float(row[2]) - 0.75
        ymin = float(row[4]) - 0.75
        xmax = float(row[1]) + 0.75
        ymax = float(row[3]) + 1.5
        bbox = "%s,%s,%s,%s" % (xmin, ymin, xmax, ymax)
        sel = row[0].lower()
        save('custom', '%scomp.png' % (sel,), '%srad' % (sel,), ts, bbox)


def main(argv):
    """Go Main Go"""
    ts = utc()
    if len(argv) == 6:
        ts = utc(
            int(argv[1]), int(argv[2]), int(argv[3]),
            int(argv[4]), int(argv[5])
        )
    runtime(ts)


if __name__ == '__main__':
    main(sys.argv)
