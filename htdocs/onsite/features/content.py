#!/usr/bin/env python
"""Frontend for Feature Content, such that we can make some magic happen"""
import sys
import os
import re
import datetime

from pyiem.util import get_dbconn, ssw

PATTERN = re.compile(("^/onsite/features/(?P<yyyy>[0-9]{4})/(?P<mm>[0-9]{2})/"
                      "(?P<yymmdd>[0-9]{6})(?P<extra>.*)."
                      "(?P<suffix>png|gif|jpg|xls|pdf|gnumeric|mp4)$"))


def send_content_type(val, size=0, totalsize=0):
    """Do as I say"""
    # ssw("Accept-Ranges: bytes\n")
    if size > 0:
        ssw("Content-Length: %.0f\n" % (size, ))
    #if (totalsize > 0 and os.environ.get("HTTP_RANGE") and
    #        os.environ.get("HTTP_RANGE") != "bytes=0-"):
    #    ssw("Content-Range: %s/%s\n" % (
    #        os.environ.get("HTTP_RANGE", "").replace("=", " "), totalsize))
    if val == 'text':
        ssw("Content-type: text/plain\n\n")
    elif val in ['png', 'gif', 'jpg']:
        ssw("Content-type: image/%s\n\n" % (val, ))
    elif val in ['mp4', ]:
        ssw("Content-type: video/%s\n\n" % (val, ))
    else:
        ssw("Content-type: text/plain\n\n")


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


def process(env):
    """Process this request

    This should look something like "/onsite/features/2016/11/161125.png"
    """
    uri = env.get('REQUEST_URI')
    if uri is None:
        send_content_type("text")
        ssw("ERROR!")
        return
    match = PATTERN.match(uri)
    if match is None:
        send_content_type("text")
        ssw("ERROR!")
        sys.stderr.write("feature content failure: %s\n" % (repr(uri), ))
        return
    data = match.groupdict()
    fn = ("/mesonet/share/features/%(yyyy)s/%(mm)s/"
          "%(yymmdd)s%(extra)s.%(suffix)s") % data
    if os.path.isfile(fn):
        #rng = env.get("HTTP_RANGE", "bytes=0-")
        #tokens = rng.replace("bytes=", "").split("-", 1)
        #stripe = slice(
        #    int(tokens[0]),
        #    (int(tokens[-1]) + 1) if tokens[-1] != '' else None)
        #sys.stderr.write(str(stripe)+"\n")
        stripe = slice(0, None)
        resdata = open(fn, 'rb').read()
        send_content_type(data['suffix'], len(resdata[stripe]), len(resdata))
        ssw(resdata[stripe])
        dblog(data['yymmdd'])
    else:
        send_content_type('png')
        from io import BytesIO
        from pyiem.plot.use_agg import plt
        (_, ax) = plt.subplots(1, 1)
        ax.text(0.5, 0.5, "Feature Image was not Found!",
                transform=ax.transAxes, ha='center')
        plt.axis('off')
        ram = BytesIO()
        plt.savefig(ram, format='png')
        ram.seek(0)
        ssw(ram.read())


def main():
    """Do Something"""
    process(os.environ)


if __name__ == '__main__':
    main()
