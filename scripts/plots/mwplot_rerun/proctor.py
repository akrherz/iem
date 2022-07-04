"""
Drive the reprocessing of the MWcomp plot.  We are doing this since our
data archives have more data than the stuff I previously got from NSSL
"""
import subprocess
import datetime
import os
from pyiem.util import get_dbconn

ASOS = get_dbconn("asos")
acursor = ASOS.cursor()

min10 = datetime.timedelta(minutes=10)


def metar_extract(now):
    """
    Giveme a METAR file with the data we have in the coffers
    """
    acursor.execute(
        """
    SELECT metar from t%s WHERE valid BETWEEN '%s+00' and '%s+00'
    and metar is not null and length(station) = 4
    """
        % (
            now.year,
            (now - min10).strftime("%Y-%m-%d %H:%M"),
            (now + min10).strftime("%Y-%m-%d %H:%M"),
        )
    )
    output = open("metar.txt", "w")
    output.write("\x01\r\r\n")
    output.write("000 \r\r\n")
    output.write("SAUS99 KISU %s\r\r\n" % (now.strftime("%d%H%M"),))
    output.write("METAR\r\r\n")
    for row in acursor:
        output.write(row[0] + "=\r\r\n")
    output.write("\x03\r\r\n")
    output.close()


def process_metar(now):
    """
    Generate the GEMPAK file!
    """
    if os.path.isfile("metar.gem"):
        os.unlink("metar.gem")
    cmd = "cat metar.txt | dcmetr -c %s metar.gem" % (
        now.strftime("%Y%m%d/%H%M"),
    )
    subprocess.call(cmd, shell=True)


def generate_image(now):
    """
    Generate the GEMPAK file!
    """
    cmd = "csh mwplot.csh %s" % (now.strftime("%Y %m %d %H %M"),)
    subprocess.call(cmd, shell=True)


def cleanup():
    """delete temp stuff"""
    for fn in [
        "MWmesonet.gif",
        "dcmetr.log",
        "gdcntr.out",
        "gddelt.out",
        "gemglb.nts",
        "last.nts",
        "metar.gem",
        "metar.txt",
        "oabsfc.out",
        "sfmap.out",
    ]:
        if os.path.isfile(fn):
            os.remove(fn)


for year in range(2005, 2009):
    for month in (1, 4, 7, 10):
        for hour in range(24):
            now = datetime.datetime(year, month, 15, hour)
            print(now)
            metar_extract(now)
            process_metar(now)
            generate_image(now)
            cleanup()
