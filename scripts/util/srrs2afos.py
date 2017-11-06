"""Ingest the SRRS text files into the AFOS IEM database"""
from __future__ import print_function
import glob
import datetime
import tarfile
import subprocess
import re
import sys
import os

import pytz
from pyiem.util import noaaport_text, get_dbconn
from pyiem.nws.product import TextProduct

BAD_CHARS = r"[^\na-zA-Z0-9:\(\)\%\.,\s\*\-\?\|/><&$=\+\@#]"
DELIMITER = re.compile(r"[\*#]{4}[0-9]{9,10}[\*#]{4}")
ENDDELIM = "****0000000000****"

PGCONN = get_dbconn('afos')


def process():
    """ Process this timestamp """
    for tarfn in glob.glob("9957*tar.Z"):
        cursor = PGCONN.cursor()
        subprocess.call("uncompress %s" % (tarfn,), shell=True)
        ts = datetime.datetime.strptime(tarfn[9:17], '%Y%m%d')
        ts = ts.replace(hour=23, minute=59, tzinfo=pytz.utc)
        tar = tarfile.open(tarfn[:-2], 'r')
        memory = []
        for member in tar.getmembers():
            fobj = tar.extractfile(member)
            content = re.sub(BAD_CHARS, "", fobj.read()) + ENDDELIM
            pos = 0
            good = 0
            bad = 0
            deleted = 0
            for match in re.finditer(DELIMITER, content):
                pos1 = match.start()
                bulletin = "000 \r\r" + content[pos:pos1]
                pos = match.end()
                if len(bulletin) < 20:
                    bad += 1
                    continue
                bulletin = noaaport_text(bulletin)
                try:
                    prod = TextProduct(bulletin, utcnow=ts,
                                       parse_segments=False)
                except Exception as exp:
                    bad += 1
                    print('Parsing Failure %s\n%s' % (fobj.name, exp))
                    continue

                if prod.valid.year != ts.year:
                    bad += 1
                    print('Invalid timestamp, year mismatch')
                    continue

                table = "products_%s_%s" % (prod.valid.year,
                                            ("0712" if prod.valid.month > 6
                                             else "0106"))
                key = "%s_%s_%s" % (prod.afos,
                                    prod.valid.strftime("%Y%m%d%H%M"),
                                    prod.source)
                if key not in memory:
                    cursor.execute("""
                    DELETE from """ + table + """ WHERE pil = %s and
                    entered = %s and source = %s
                    """, (prod.afos, prod.valid, prod.source))
                    deleted += cursor.rowcount
                    memory.append(key)
                cursor.execute("""INSERT into """+table+"""
            (data, pil, entered, source, wmo) values (%s,%s,%s,%s,%s)
            """, (bulletin, prod.afos, prod.valid, prod.source, prod.wmo))
                good += 1
        subprocess.call("compress %s" % (tarfn[:-2],), shell=True)
        print(("Processed %s Good: %s Bad: %s Deleted: %s"
               ) % (tarfn, good, bad, deleted))
        if len(content) > 1000 and good < 5:
            print("ABORT!")
            sys.exit()

        cursor.close()
        PGCONN.commit()


def main():
    """ Go Main Go """
    os.chdir("/mesonet/tmp/ncei")
    for order in glob.glob("HAS*"):
        os.chdir(order)
        process()
        os.chdir("..")


if __name__ == '__main__':
    # do something
    main()
