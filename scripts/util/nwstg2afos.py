"""Ingest the NWSTG text files into the AFOS IEM database
"""
from __future__ import print_function
import glob
import datetime
import tarfile
import subprocess
import re
import os

import pytz
from pyiem.util import noaaport_text, get_dbconn
from pyiem.nws.product import TextProduct

BAD_CHARS = r"[^\na-zA-Z0-9:\(\)\%\.,\s\*\-\?\|/><&$=\+\@]"

PGCONN = get_dbconn('afos')


def process(order):
    """ Process this timestamp """
    cursor = PGCONN.cursor()
    for tarfn in glob.glob("NWSTG*tar.Z"):
        subprocess.call("uncompress %s" % (tarfn,), shell=True)
        ts = datetime.datetime.strptime(tarfn[6:14], '%Y%m%d')
        ts = ts.replace(hour=23, minute=59, tzinfo=pytz.utc)
        tar = tarfile.open(tarfn[:-2], 'r')
        memory = []
        for member in tar.getmembers():
            fobj = tar.extractfile(member)
            if not fobj.name.startswith("TEXT_"):
                continue
            content = (re.sub(BAD_CHARS, "",
                              fobj.read())).replace("\r\r", "")
            parts = fobj.name.strip().split("_")
            ttaaii = parts[1]
            source = parts[2]
            delimiter = "%s %s" % (ttaaii, source)
            # Filter content back to the start of the ttaaii
            pos = content.find(delimiter)
            if pos == -1:
                print(('Skipping can not find %s in product %s'
                       ) % (delimiter, fobj.name))
                continue
            content = content[pos:]
            # Now we are getting closer, lets split by the delimter as we
            # may have multiple products in one file!
            for bulletin in content.split(delimiter):
                if len(bulletin) == 0:
                    continue
                bulletin = "000\n%s%s" % (delimiter, bulletin)
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
            """, (bulletin, prod.afos, prod.valid, source, ttaaii))
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
