"""Ingest the SRRS text files into the AFOS IEM database
"""
from __future__ import print_function
import glob
import datetime
import tarfile
import subprocess
import re
import os

import psycopg2
import pytz
from pyiem.util import noaaport_text
from pyiem.nws.product import TextProduct

BAD_CHARS = r"[^\na-zA-Z0-9:\(\)\%\.,\s\*\-\?\|/><&$=\+\@]"
DELIMITER = re.compile(r"\*\*\*\*[0-9]{10}\*\*\*\*")
ENDDELIM = "****0000000000****"

PGCONN = psycopg2.connect(database='afos', host='iemdb')


def process(order):
    """ Process this timestamp """
    cursor = PGCONN.cursor()
    for tarfn in glob.glob("9957*tar.Z"):
        subprocess.call("uncompress %s" % (tarfn,), shell=True)
        ts = datetime.datetime.strptime(tarfn[9:17], '%Y%m%d')
        ts = ts.replace(hour=23, minute=59, tzinfo=pytz.utc)
        tar = tarfile.open(tarfn[:-2], 'r')
        memory = []
        for member in tar.getmembers():
            fobj = tar.extractfile(member)
            content = re.sub(BAD_CHARS, "", fobj.read()) + ENDDELIM
            pos = 0
            for match in re.finditer(DELIMITER, content):
                pos1 = match.start()
                bulletin = "000 \r\r" + content[pos:pos1]
                pos = match.end()
                if len(bulletin) < 20:
                    continue
                bulletin = noaaport_text(bulletin)
                try:
                    prod = TextProduct(bulletin, utcnow=ts,
                                       parse_segments=False)
                except Exception as exp:
                    print('Parsing Failure %s\n%s' % (fobj.name, exp))
                    continue

                if prod.valid.year != ts.year:
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
                    memory.append(key)
                cursor.execute("""INSERT into """+table+"""
            (data, pil, entered, source, wmo) values (%s,%s,%s,%s,%s)
            """, (bulletin, prod.afos, prod.valid, prod.source, prod.wmo))
        subprocess.call("compress %s" % (tarfn[:-2],), shell=True)

    cursor.close()
    PGCONN.commit()


def main():
    """ Go Main Go """
    os.chdir("/mesonet/tmp/ncei")
    for order in glob.glob("HAS*"):
        os.chdir(order)
        process(order)
        os.chdir("..")


if __name__ == '__main__':
    # do something
    main()
