#!/usr/bin/env python
"""Frontend for Feature Content, such that we can make some magic happen"""
import sys
import os
import re
import datetime

from pyiem.util import get_dbconn

PATTERN = re.compile(("^/onsite/features/(?P<yyyy>[0-9]{4})/(?P<mm>[0-9]{2})/"
                      "(?P<yymmdd>[0-9]{6})(?P<extra>.*)."
                      "(?P<suffix>png|gif|xls|pdf|gnumeric)$"))


def send_content_type(val):
    """Do as I say"""
    if val == 'text':
        sys.stdout.write("Content-type: text/plain\n\n")
    elif val in ['png', 'gif']:
        sys.stdout.write("Content-type: image/%s\n\n" % (val,))
    else:
        sys.stdout.write("Content-type: text/plain\n\n")


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
        sys.stdout.write("ERROR!")
        return
    match = PATTERN.match(uri)
    if match is None:
        send_content_type("text")
        sys.stdout.write("ERROR!")
        sys.stderr.write("feature content failure: %s\n" % (repr(uri), ))
        return
    data = match.groupdict()
    fn = ("/mesonet/share/features/%(yyyy)s/%(mm)s/"
          "%(yymmdd)s%(extra)s.%(suffix)s") % data
    if os.path.isfile(fn):
        send_content_type(data['suffix'])
        sys.stdout.write(open(fn, 'rb').read())
        dblog(data['yymmdd'])
    else:
        send_content_type('png')
        import cStringIO
        import matplotlib
        matplotlib.use('agg')
        import matplotlib.pyplot as plt
        (_, ax) = plt.subplots(1, 1)
        ax.text(0.5, 0.5, "Feature Image was not Found!",
                transform=ax.transAxes, ha='center')
        plt.axis('off')
        ram = cStringIO.StringIO()
        plt.savefig(ram, format='png')
        ram.seek(0)
        sys.stdout.write(ram.read())


def main():
    """Do Something"""
    process(os.environ.get('REQUEST_URI'))


if __name__ == '__main__':
    main()
