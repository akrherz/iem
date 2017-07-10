"""Download and archive 1000 ft reflectivity from the NCEP HRRR"""
from __future__ import print_function
import sys
import os
import datetime
import urllib2

import pytz
import pygrib

# 18 hours of output + analysis
COMPLETE_GRIB_MESSAGES = 18 * 4 + 1


def upstream_has_data(valid):
    """Does data exist upstream to even attempt a download"""
    utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    # NCEP should have at least 24 hours of data
    return (utcnow - datetime.timedelta(hours=24)) < valid


def run(valid):
    """ run for this valid time! """
    if not upstream_has_data(valid):
        return
    gribfn = valid.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
                             "hrrr.t%Hz.refd.grib2"))
    if os.path.isfile(gribfn):
        # See how many grib messages we have
        try:
            grbs = pygrib.open(gribfn)
            if grbs.messages == COMPLETE_GRIB_MESSAGES:
                return
            del grbs
        except Exception as exp:
            pass
    output = open(gribfn, 'wb')
    for hr in range(0, 19):
        shr = "%02i" % (hr,)
        uri = valid.strftime(("http://www.ftp.ncep.noaa.gov/data/nccf/"
                              "com/hrrr/prod/"
                              "hrrr.%Y%m%d/hrrr.t%Hz.wrfsubhf" + shr +
                              ".grib2.idx"))
        attempt = 0
        data = None
        while data is None and attempt < 10:
            try:
                data = urllib2.urlopen(uri, timeout=30).readlines()
            except Exception as exp:
                print("dl_hrrrref FAIL %s %s %s %s" % (valid, hr, exp, uri))
            attempt += 1
        if data is None:
            print("ABORT")
            sys.exit()

        offsets = []
        neednext = False
        for line in data:
            tokens = line.split(":")
            if neednext:
                offsets[-1].append(int(tokens[1]))
                neednext = False
            if tokens[3] == 'REFD' and tokens[4] == '1000 m above ground':
                offsets.append([int(tokens[1])])
                neednext = True

        req = urllib2.Request(uri[:-4])

        if hr > 0 and len(offsets) != 4:
            print(("dl_hrrrref[%s] hr: %s offsets: %s"
                   ) % (valid.strftime("%Y%m%d%H"), hr, offsets))
        for pr in offsets:
            req.headers['Range'] = 'bytes=%s-%s' % (pr[0], pr[1])
            fp = None
            attempt = 0
            while fp is None and attempt < 10:
                try:
                    fp = urllib2.urlopen(req)
                except Exception as exp:
                    print("dl_hrrrref FAIL %s %s %s %s" % (valid, hr, exp,
                                                           req))
                attempt += 1
            if fp is None:
                continue
            output.write(fp.read())

    output.close()


def main():
    """ Go Main Go """
    valid = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                              int(sys.argv[3]), int(sys.argv[4]))
    valid = valid.replace(tzinfo=pytz.utc)
    run(valid)
    # in case we missed some old data, re-download
    run(valid - datetime.timedelta(hours=12))


if __name__ == '__main__':
    # do main
    main()
