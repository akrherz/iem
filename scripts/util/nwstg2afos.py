"""Ingest the NWSTG text files into the AFOS IEM database
"""
import psycopg2
import datetime
import sys
import tarfile
import subprocess
import pytz
import re
import os
from pyiem.nws.product import TextProduct

BAD_CHARS = "[^\na-zA-Z0-9:\(\)\%\.,\s\*\-\?\|/><&$=\+\@]"

PGCONN = psycopg2.connect(database='afos', host='iemdb')


def find_awipsid(data):
    """ Attempt to guess the AWIPSID """
    tokens = re.findall("[0-9]{6}\s+([A-Z][A-Z][A-Z0-9][A-Z0-9]{1,3})", data)
    if len(tokens) == 0:
        return None
    return tokens[0]


def do(ts):
    """ Process this timestamp """
    cursor = PGCONN.cursor()

    fn = ts.strftime("/mnt/mesonet2/data/nwstg/NWSTG_%Y%m%d.tar.Z")
    if not os.path.isfile(fn):
        print("MISSING FILE: %s" % (fn,))
        return
    subprocess.call("uncompress %s" % (fn,), shell=True)
    tar = tarfile.open(fn[:-2], 'r')
    for member in tar.getmembers():
        f = tar.extractfile(member)
        tar2 = tarfile.open(fileobj=f, mode='r')
        for member2 in tar2.getmembers():
            f2 = tar2.extractfile(member2)
            if not f2.name.startswith("TEXT_"):
                continue
            content = (re.sub(BAD_CHARS, "", f2.read())).replace("\r\r", "")
            parts = f2.name.strip().split("_")
            ttaaii = parts[1]
            source = parts[2]
            if source[0] not in ['K', 'P']:
                continue
            if source in ['KWBC', 'KWAL']:
                continue
            delimiter = "%s %s" % (ttaaii, source)
            # Filter content back to the start of the ttaaii
            pos = content.find(delimiter)
            if pos == -1:
                print 'Skipping can not find %s in product %s' % (delimiter,
                                                                  f2.name)
                continue
            content = content[pos:]
            awipsid = find_awipsid(content)
            if (awipsid is not None and 
                (awipsid.startswith("RR") or awipsid.startswith("MTR")
                 or awipsid in ["TSTNCF", "WTSNCF"])):
                print 'Skip', f2.name, awipsid
                continue
            # Now we are getting closer, lets split by the delimter as we 
            # may have multiple products in one file!
            for bulletin in content.split(delimiter):
                if len(bulletin) == 0:
                    continue
                bulletin = "000\n%s%s" % (delimiter, bulletin)
                try:
                    prod = TextProduct(bulletin, utcnow=ts)
                except:
                    print 'Parsing Failure', f2.name
                    continue

                if prod.valid.year != ts.year:
                    print 'Invalid timestamp, year mismatch'
                    continue

                table = "products_%s_%s" % (prod.valid.year, 
                                        "0712" if prod.valid.month > 6 else "0106")

                print 'SAVE', f2.name, prod.valid.strftime("%Y%m%d%H%M"), awipsid, prod.afos, table
                cursor.execute("""INSERT into """+table+"""
            (data, pil, entered, source, wmo) values (%s,%s,%s,%s,%s)""",
            (bulletin, prod.afos, prod.valid, source, ttaaii))

    cursor.close()
    PGCONN.commit()
    subprocess.call("compress %s" % (fn[:-2],), shell=True)


def main():
    """ Go Main Go """
    sts = datetime.datetime( int(sys.argv[1]), int(sys.argv[2]),
                             int(sys.argv[3]))
    ets = datetime.datetime( int(sys.argv[4]), int(sys.argv[5]),
                             int(sys.argv[6]))
    now = sts
    while now <= ets:
        do(now.replace(tzinfo=pytz.timezone("UTC")))
        now += datetime.timedelta(days=1)


if __name__ == '__main__':
    # do something
    main()
