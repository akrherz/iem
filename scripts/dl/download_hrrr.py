"""
 Since the NOAAPort feed of HRRR data does not have radiation, we should
 download this manually from NCEP

Run at 40 AFTER for the previous hour

"""
import subprocess
import sys
import datetime
import os

import requests
import pygrib
from pyiem.util import exponential_backoff, logger
LOG = logger()


def need_to_run(valid):
    """ Check to see if we already have the radiation data we need"""
    gribfn = valid.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/"
                             "%H/hrrr.t%Hz.3kmf00.grib2"))
    if not os.path.isfile(gribfn):
        return True
    try:
        grbs = pygrib.open(gribfn)
        for name in ['Downward short-wave radiation flux',
                     'Upward long-wave radiation flux']:
            grbs.select(name=name)
        # print("%s had everything we desired!" % (gribfn, ))
        return False
    except Exception:
        return True


def fetch(valid):
    """ Fetch the radiation data for this timestamp
    80:54371554:d=2014101002:ULWRF:top of atmosphere:anl:
    81:56146124:d=2014101002:DSWRF:surface:anl:
    """
    uri = valid.strftime(("http://www.ftp.ncep.noaa.gov/data/nccf/"
                          "com/hrrr/prod/hrrr.%Y%m%d/conus/hrrr.t%Hz."
                          "wrfprsf00.grib2.idx"))
    req = requests.get(uri, timeout=30)
    if req.status_code != 200:
        LOG.info("failed to get idx %s", uri)
        return

    offsets = []
    neednext = False
    for line in req.content.decode('utf-8').split("\n"):
        tokens = line.split(":")
        if len(tokens) < 3:
            continue
        if neednext:
            offsets[-1].append(int(tokens[1]))
            neednext = False
        if tokens[3] in ['ULWRF', 'DSWRF']:
            offsets.append([int(tokens[1]), ])
            neednext = True
        # Save soil temp and water at surface, 10cm and 40cm
        if tokens[3] in ['TSOIL', 'SOILW']:
            if tokens[4] in ['0-0 m below ground',
                             '0.1-0.1 m below ground',
                             '0.3-0.3 m below ground',
                             '0.6-0.6 m below ground',
                             '1-1 m below ground']:
                offsets.append([int(tokens[1]), ])
                neednext = True

    outfn = valid.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/"
                            "%H/hrrr.t%Hz.3kmf00.grib2"))
    outdir = os.path.dirname(outfn)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)  # make sure LDM can then write to dir
        subprocess.call("chmod 775 %s" % (outdir, ), shell=True)
    output = open(outfn, 'ab', 0o664)

    if len(offsets) != 13:
        LOG.info("warning, found %s gribs for %s", len(offsets), valid)
    for pr in offsets:
        headers = {'Range': 'bytes=%s-%s' % (pr[0], pr[1])}
        req = exponential_backoff(requests.get, uri[:-4],
                                  headers=headers, timeout=30)
        if req is None:
            LOG.info("failure for uri: %s", uri)
        else:
            output.write(req.content)

    output.close()


def main():
    """ Go Main Go"""
    times = []
    if len(sys.argv) == 5:
        times.append(datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                                       int(sys.argv[3]), int(sys.argv[4])))
    else:
        times.append(datetime.datetime.utcnow() - datetime.timedelta(hours=1))
        times.append(datetime.datetime.utcnow() - datetime.timedelta(hours=6))
        times.append(datetime.datetime.utcnow() - datetime.timedelta(hours=24))
    for ts in times:
        if not need_to_run(ts):
            continue
        fetch(ts)


if __name__ == '__main__':
    os.umask(0o002)
    main()
