"""
 Need something to ingest the CTRE provided bridge data
  RSAI4
  RLRI4
 Run from RUN_1MIN
"""
from __future__ import print_function
import datetime
import sys
from io import BytesIO
import ftplib
import subprocess

import pytz
import pyiem.util as util
from pyiem.observation import Observation


def main():
    """Go Main Go"""
    # Run every 3 minutes
    now = datetime.datetime.now()
    if now.minute % 4 != 0 and len(sys.argv) < 2:
        return

    props = util.get_properties()
    pgconn = util.get_dbconn("iem")
    icursor = pgconn.cursor()

    csv = open("/tmp/ctre.txt", "w")
    bio = BytesIO()
    # Get Saylorville
    try:
        ftp = ftplib.FTP("129.186.224.167")
        ftp.login(props["ctre_ftpuser"], props["ctre_ftppass"])
        ftp.retrbinary("RETR Saylorville_Table3Min_current.dat", bio.write)
        ftp.close()
    except Exception as exp:
        if now.minute % 15 == 0:
            print("Download CTRE Bridge Data Failed!!!\n%s" % (exp,))
        return
    bio.seek(0)
    data = bio.getvalue().decode("ascii").split("\n")
    bio.truncate()
    if len(data) < 2:
        return
    keys = data[0].strip().replace('"', "").split(",")
    vals = data[1].strip().replace('"', "").split(",")
    d = {}
    for i, val in enumerate(vals):
        d[keys[i]] = val
    # Ob times are always CDT
    ts1 = datetime.datetime.strptime(d["TIMESTAMP"], "%Y-%m-%d %H:%M:%S")
    gts1 = ts1 + datetime.timedelta(hours=5)
    gts1 = gts1.replace(tzinfo=pytz.UTC)
    lts = gts1.astimezone(pytz.timezone("America/Chicago"))

    iem = Observation("RSAI4", "OT", lts)
    drct = d["WindDir"]
    iem.data["drct"] = drct
    sknt = float(d["WS_mph_S_WVT"]) / 1.15
    iem.data["sknt"] = sknt
    gust = float(d["WS_mph_Max"]) / 1.15
    iem.data["gust"] = gust
    iem.save(icursor)

    csv.write(
        "%s,%s,%s,%.1f,%.1f\n"
        % ("RSAI4", gts1.strftime("%Y/%m/%d %H:%M:%S"), drct, sknt, gust)
    )

    # Red Rock
    try:
        ftp = ftplib.FTP("129.186.224.167")
        ftp.login(props["ctre_ftpuser"], props["ctre_ftppass"])
        ftp.retrbinary("RETR Red Rock_Table3Min_current.dat", bio.write)
        ftp.close()
    except Exception as exp:
        if now.minute % 15 == 0:
            print("Download CTRE Bridge Data Failed!!!\n%s" % (exp,))
        return
    bio.seek(0)
    data = bio.getvalue().decode("ascii").split("\n")
    bio.truncate()
    if len(data) < 2:
        return

    keys = data[0].strip().replace('"', "").split(",")
    vals = data[1].strip().replace('"', "").split(",")
    d = {}
    for i, val in enumerate(vals):
        d[keys[i]] = val

    ts2 = datetime.datetime.strptime(d["TIMESTAMP"], "%Y-%m-%d %H:%M:%S")
    gts2 = ts2 + datetime.timedelta(hours=5)
    gts2 = gts2.replace(tzinfo=pytz.UTC)
    lts = gts2.astimezone(pytz.timezone("America/Chicago"))

    iem = Observation("RLRI4", "OT", lts)
    drct = d["WindDir"]
    iem.data["drct"] = drct
    sknt = float(d["WS_mph_S_WVT"]) / 1.15
    iem.data["sknt"] = sknt
    gust = float(d["WS_mph_Max"]) / 1.15
    iem.data["gust"] = gust
    iem.save(icursor)

    csv.write(
        "%s,%s,%s,%.1f,%.1f\n"
        % ("RLRI4", gts2.strftime("%Y/%m/%d %H:%M:%S"), drct, sknt, gust)
    )

    csv.close()

    cmd = (
        "pqinsert -i -p 'data c %s csv/ctre.txt " "bogus txt' /tmp/ctre.txt"
    ) % (now.strftime("%Y%m%d%H%M"),)
    subprocess.call(cmd, shell=True)

    icursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
