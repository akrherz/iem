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
import os
import sys
import subprocess

from pyiem.util import get_properties, logger

LOG = logger()
PROPS = get_properties()


def trans(now):
    """Hacky hack hack"""
    if now.year < 1992:
        return "100"
    if now.year < 2001:
        return "200"
    if now.year < 2011:
        return "300"
    return "400"


def do_month(sts):
    """Run for a given month"""

    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)

    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        LOG.debug(now)
        # We only fetch the northern hemisphere, for better or worse
        uri = now.strftime(
            "http://goldsmr4.gesdisc.eosdis.nasa.gov/daac-bin/OTF/"
            "HTTP_services.cgi?FILENAME=/data/s4pa/MERRA2"
            f"/M2T1NXRAD.5.12.4/%Y/%m/MERRA2_{trans(now)}.tavg1_2d_rad_"
            "Nx.%Y%m%d.nc4&FORMAT=bmM0Lw&"
            "BBOX=0,-180,90,180&"
            f"LABEL=MERRA2_{trans(now)}.tavg1_2d_rad_Nx.%Y%m%d.SUB.nc"
            "&FLAGS=&SHORTNAME=M2T1NXRAD&SERVICE=L34RS_MERRA2&"
            "LAYERS=&VERSION=1.02&VARIABLES=swgdn,swgdnclr,swtdn"
        )
        dirname = now.strftime("/mesonet/data/merra2/%Y")
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        localfn = now.strftime("/mesonet/data/merra2/%Y/%Y%m%d.nc")
        cmd = (
            "curl -n -c ~/.urscookies -b ~/.urscookies -L "
            f"--url '{uri}' -o {localfn}"
        )
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE
        ) as proc:
            proc.stderr.read()
        now += interval


def main(argv):
    """Run for last month month"""
    now = datetime.datetime.now()
    if len(argv) == 3:
        now = datetime.datetime(int(argv[1]), int(argv[2]), 1)
    else:
        now = now - datetime.timedelta(days=35)
        now = now.replace(day=1)
    do_month(now)


if __name__ == "__main__":
    main(sys.argv)
