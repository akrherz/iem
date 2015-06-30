"""
 Since the NOAAPort feed of HRRR data does not have radiation, we should
 download this manually from NCEP

Run at 40 AFTER for the previous hour

"""
import urllib2
import sys
import datetime
import os


def fetch(valid):
    """ Fetch the radiation data for this timestamp
    80:54371554:d=2014101002:ULWRF:top of atmosphere:anl:
    81:56146124:d=2014101002:DSWRF:surface:anl:
    """

    uri = valid.strftime(("http://www.ftp.ncep.noaa.gov/data/nccf/"
                          "nonoperational/com/hrrr/prod/hrrr.%Y%m%d/hrrr.t%Hz."
                          "wrfprsf00.grib2.idx"))
    data = urllib2.urlopen(uri, timeout=30)

    offsets = []
    neednext = False
    for line in data:
        tokens = line.split(":")
        if neednext:
            offsets[-1].append(int(tokens[1]))
            neednext = False
        if tokens[3] in ['ULWRF', 'DSWRF']:
            offsets.append([int(tokens[1]), ])
            neednext = True
        # Save soil temp and water at surface, 10cm and 40cm
        if tokens[3] in ['TSOIL', 'SOILW']:
            if tokens[4] in ['0-0 m below ground',
                             '0.01-0.01 m below ground',
                             '0.04-0.04 m below ground']:
                offsets.append([int(tokens[1]), ])
                neednext = True

    outfn = valid.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/"
                            "%H/hrrr.t%Hz.3kmf00.grib2"))
    outdir = os.path.dirname(outfn)
    if not os.path.isdir(outdir):
        os.makedirs(outdir, mode=0775)  # make sure LDM can then write to dir
    output = open(outfn, 'ab', 0664)

    req = urllib2.Request(uri[:-4])
    if len(offsets) != 8:
        print("download_hrrr_rad warning, found %s gribs for %s" % (
                                                    len(offsets), valid))
    for pr in offsets:
        req.headers['Range'] = 'bytes=%s-%s' % (pr[0], pr[1])
        f = urllib2.urlopen(req, timeout=30)
        output.write(f.read())

    output.close()


def main():
    """ Go Main Go"""
    ts = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    if len(sys.argv) == 5:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]), int(sys.argv[4]))
    fetch(ts)


if __name__ == '__main__':
    os.umask(0002)
    main()
