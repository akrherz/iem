"""
 Monthly download of the MERRA data, website suggests that the previous
 month is available around the 2-3 week of the next month, so this is run
 from RUN_MIDNIGHT.sh, but only on the 21rst of each month
"""
import datetime
import urllib2
import os
import sys
import subprocess


def trans(now):
    """ Hacky hack hack """
    if now.year < 1993:
        return '101'
    if now.year < 2001:
        return '201'
    return '300'


def do_month(sts):
    """ Run for a given month """

    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)

    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        uri = now.strftime(
            ("http://goldsmr2.sci.gsfc.nasa.gov/daac-bin/OTF/"
             "HTTP_services.cgi?FILENAME=%%2Fdata%%2Fs4pa%%2FMERRA%%2"
             "FMAT1NXRAD.5.2.0%%2F%Y%%2F%m%%2FMERRA"+trans(now)+".prod.assim."
             "tavg1_2d_rad_Nx.%Y%m%d.hdf&FORMAT=TmV0Q0RGL2d6aXAv&"
             "BBOX=22.852,-129.727,52.383,-60.117&LABEL=MERRA" +
             trans(now) + ".prod.assim.tavg1_2d_rad_Nx.%Y%m%d.SUB.nc.gz&"
             "FLAGS=&SHORTNAME=MAT1NXRAD&SERVICE=SUBSET_LATS4D&LAYERS=&"
             "VERSION=1.02&VARIABLES=swtdn,swgdn,swgdnclr,tauhgh,taulow,"
             "taumid,tautot,cldhgh,cldlow,cldmid,cldtot"))

        try:
            req = urllib2.Request(uri)
            data = urllib2.urlopen(req).read()
        except:
            uri = uri.replace("MERRA300", "MERRA301")
            req = urllib2.Request(uri)
            data = urllib2.urlopen(req).read()
        dirname = now.strftime("/mesonet/merra/%Y")
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        fp = open(now.strftime("/mesonet/merra/%Y/%Y%m%d.nc.gz"), 'w')
        fp.write(data)
        fp.close()
        now += interval

    os.chdir(dirname)
    subprocess.call("gunzip *.gz", shell=True)


def main():
    """ Run for last month month """
    now = datetime.datetime.now()
    if len(sys.argv) == 3:
        now = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), 1)
    else:
        now = now - datetime.timedelta(days=35)
        now = now.replace(day=1)
    do_month(now)

if __name__ == '__main__':
    main()
