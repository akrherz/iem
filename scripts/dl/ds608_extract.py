"""Extract DSWRF from CISL ArchiveStatus
http://rda.ucar.edu/datasets/ds608.0/index.html

1) Download the TAR Files from the website manually
"""
import glob
import subprocess
import pygrib
import datetime
import os

for tarfn in glob.glob("NARRsfc*.tar"):
    subprocess.call("tar -xf %s" % (tarfn, ), shell=True)
    for grbfn in glob.glob("merged_AWIP32*sfc"):
        grbs = pygrib.open(grbfn)
        for grb in grbs.select(parameterName='204', stepType='avg'):
            dt = grb['dataDate']
            hr = int(grb['dataTime']) / 100
            ts = datetime.datetime.strptime("%s %s" % (dt, hr), "%Y%m%d %H")
            fn = "rad_%s.grib" % (ts.strftime("%Y%m%d%H%M"), )
            o = open(fn, 'wb')
            o.write(grb.tostring())
            o.close()

            cmd = ("/home/ldm/bin/pqinsert -p 'data a %s bogus "
                   "model/NARR/rad_%s.grib grib' %s"
                   ) % (ts.strftime("%Y%m%d%H%M"),
                        ts.strftime("%Y%m%d%H%M"), fn)
            subprocess.call(cmd, shell=True)
            print grbfn, fn
            os.remove(fn)
        os.remove(grbfn)
