"""
 Monthly download of the MERRA data, website suggests that the previous
 month is available around the 2-3 week of the next month, so this is run
 from RUN_MIDNIGHT.sh, but only on the 21rst of each month

MERRA2 Variables we want to process
-----------------------------------
http://goldsmr4.sci.gsfc.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/doc/
MERRA2.README.pdf

(M2T1NXRAD)
SWGDNCLR    surface incoming shortwave flux assuming clear sky
SWTDN       toa incoming shortwave flux
SWGDN       surface incoming shortwave flux
SWGDNCLR    surface incoming shortwave flux assuming clear sky
"""
import datetime
import urllib2
import os
import sys


def trans(now):
    """ Hacky hack hack """
    if now.year < 1993:
        return '100'
    if now.year < 2001:
        return '200'
    if now.year < 2011:
        return '300'
    return '400'


def do_month(sts):
    """ Run for a given month """

    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)

    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        uri = now.strftime(
            ("http://goldsmr4.gesdisc.eosdis.nasa.gov/daac-bin/OTF/"
             "HTTP_services.cgi?FILENAME=/data/s4pa/MERRA2"
             "/M2T1NXRAD.5.12.4/%Y/%m/MERRA2_"+trans(now)+".tavg1_2d_rad_"
             "Nx.%Y%m%d.nc4&FORMAT=bmM0Lw&"
             "BBOX=22.852,-129.727,52.383,-60.117"
             "&LABEL=MERRA2_"+trans(now)+".tavg1_2d_rad_Nx.%Y%m%d.SUB.nc"
             "&FLAGS=&SHORTNAME=M2T1NXRAD&SERVICE=SUBSET_MERRA2&"
             "LAYERS=&VERSION=1.02&VARIABLES=swgdn,swgdnclr,swtdn"))
        try:
            req = urllib2.Request(uri)
            data = urllib2.urlopen(req).read()
        except Exception as exp:
            print uri
            print exp
            return
        dirname = now.strftime("/mesonet/merra2/%Y")
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        fp = open(now.strftime("/mesonet/merra2/%Y/%Y%m%d.nc"), 'w')
        fp.write(data)
        fp.close()
        now += interval


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
