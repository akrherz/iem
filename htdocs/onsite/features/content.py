#!/usr/bin/env python
"""Frontend for Feature Content, such that we can make some magic happen"""
import sys
import os
import re
import datetime

from pyiem.util import get_dbconn

# https://stackoverflow.com/questions/23932332
SSW = getattr(sys.stdout, 'buffer', sys.stdout).write

PATTERN = re.compile(("^/onsite/features/(?P<yyyy>[0-9]{4})/(?P<mm>[0-9]{2})/"
                      "(?P<yymmdd>[0-9]{6})(?P<extra>.*)."
                      "(?P<suffix>png|gif|xls|pdf|gnumeric)$"))


def send_content_type(val):
    """Do as I say"""
    if val == 'text':
        SSW(b"Content-type: text/plain\n\n")
    elif val in ['png', 'gif']:
        SSW(("Content-type: image/%s\n\n" % (val,)).encode('utf-8'))
    else:
        SSW(b"Content-type: text/plain\n\n")


def dblog(yymmdd):
    """Log this request"""
    try:
        pgconn = get_dbconn("mesosite")
        cursor = pgconn.cursor()
        dt = datetime.date(2000 + int(yymmdd[:2]), int(yymmdd[2:4]),
                           int(yymmdd[4:6]))
        cursor.execute("""
            UPDATE feature SET views = views + 1
            WHERE date(valid) = %s
            """, (dt,))
        pgconn.commit()
    except Exception as exp:
        sys.stderr.write(str(exp))


def process(uri):
    """Process this request

    This should look something like "/onsite/features/2016/11/161125.png"
    """
    if uri is None:
        send_content_type("text")
        SSW(b"ERROR!")
        return
    match = PATTERN.match(uri)
    if match is None:
        send_content_type("text")
        SSW(b"ERROR!")
        sys.stderr.write("feature content failure: %s\n" % (repr(uri), ))
        return
    data = match.groupdict()
    fn = ("/mesonet/share/features/%(yyyy)s/%(mm)s/"
          "%(yymmdd)s%(extra)s.%(suffix)s") % data
    if os.path.isfile(fn):
        send_content_type(data['suffix'])
        SSW(open(fn, 'rb').read())
        dblog(data['yymmdd'])
    else:
        send_content_type('png')
        from io import BytesIO
        import matplotlib
        matplotlib.use('agg')
        import matplotlib.pyplot as plt
        (_, ax) = plt.subplots(1, 1)
        ax.text(0.5, 0.5, "Feature Image was not Found!",
                transform=ax.transAxes, ha='center')
        plt.axis('off')
        ram = BytesIO()
        plt.savefig(ram, format='png')
        ram.seek(0)
        SSW(ram.read())


def main():
    """Do Something"""
    process(os.environ.get('REQUEST_URI'))


if __name__ == '__main__':
    main()
