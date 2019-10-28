"""Dump what I have stored in the AFOS database to flat files
"""
from __future__ import print_function
import datetime
import subprocess

from pyiem.util import get_dbconn

pgconn = get_dbconn("afos", user="nobody")
cursor = pgconn.cursor()

pils = (
    "LSR|FWW|CFW|TCV|RFW|FFA|SVR|TOR|SVS|SMW|MWS|"
    "NPW|WCN|WSW|EWW|FLS|FLW|SPS|SEL|SWO|FFW"
)


def sanitize(data):
    """ Regularize this product
    1) \001 is the first character, on a line by itself
    2) \003 is the last character, on a line by itself, with no trailing data
    3) those two characters appear nowhere else in the file.
    """
    # Get 'clean' lines
    lines = [
        s.strip().replace("\001", "").replace("\003", "")
        for s in data.split("\n")
    ]
    # Make sure the first line is now blank!
    if lines[0] != "":
        lines.insert(0, "")
    if lines[-1] != "":
        lines.append("")
    return "\001" + ("\r\r\n".join(lines)) + "\003"


def workflow(date):
    """ Process a given UTC date """
    table = "products_%s_%s" % (
        date.year,
        "0712" if date.month > 6 else "0106",
    )
    for pil in pils.split("|"):
        cursor.execute(
            """
            SELECT data from """
            + table
            + """ WHERE
            entered >= '%s 00:00+00' and entered < '%s 00:00+00' and
            substr(pil,1,3) = '%s' ORDER by entered ASC
            """
            % (
                date.strftime("%Y-%m-%d"),
                (date + datetime.timedelta(hours=36)).strftime("%Y-%m-%d"),
                pil,
            )
        )
        if cursor.rowcount == 0:
            continue
        print("%s %s %s" % (date, pil, cursor.rowcount))
        output = open("/tmp/afos.tmp", "w")
        for row in cursor:
            output.write(sanitize(row[0]))
        output.close()

        cmd = "data a %s0000 bogus text/noaaport/%s_%s.txt txt" % (
            date.strftime("%Y%m%d"),
            pil,
            date.strftime("%Y%m%d"),
        )
        cmd = "/home/ldm/bin/pqinsert -p '%s' /tmp/afos.tmp" % (cmd,)
        subprocess.call(cmd, shell=True)


def main():
    """Go Main"""
    sts = datetime.datetime(2000, 1, 1)
    ets = datetime.datetime(2006, 8, 4)
    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        workflow(now)
        now += interval


if __name__ == "__main__":
    # go
    main()
