#!/usr/bin/env python
"""give me some AFOS data please"""
from __future__ import print_function
import cgi
import unittest

from pyiem.util import get_dbconn, ssw


def pil_logic(s):
    """Convert the CGI pil value into something we can query

    Args:
      s (str): The CGI variable wanted

    Returns:
      list of PILs to send to the databae"""
    if s == '':
        return []
    s = s.upper()
    pils = []
    if s.find(",") == -1:
        pils.append(s)
    else:
        pils = s.split(",")

    res = []
    for pil in pils:
        if pil[:3] == "WAR":
            for q in ['FLS', 'FFS', 'AWW', 'TOR', 'SVR', 'FFW', 'SVS',
                      'LSR', 'SPS', 'WSW', 'FFA', 'WCN']:
                res.append("%s%s" % (q, pil[3:6]))
        else:
            res.append("%6.6s" % (pil.strip() + '      ', ))
    return res


def main():
    """Process the request"""
    # Attempt to keep the file from downloading and just displaying in chrome
    form = cgi.FieldStorage()
    pils = pil_logic(form.getfirst('pil', ''))
    try:
        limit = int(form.getfirst('limit', 1))
    except ValueError:
        limit = 1
    center = form.getfirst('center', '')[:4]
    sdate = form.getfirst('sdate', '')[:10]
    edate = form.getfirst('edate', '')[:10]
    ttaaii = form.getfirst('ttaaii', '')[:6]
    fmt = form.getfirst('fmt', 'text')
    ssw("X-Content-Type-Options: nosniff\n")
    if form.getfirst('dl') == "1":
        ssw("Content-type: application/octet-stream\n")
        ssw("Content-Disposition: attachment; filename=afos.txt\n\n")
    else:
        if fmt == 'text':
            ssw("Content-type: text/plain\n\n")
        elif fmt == 'html':
            ssw("Content-type: text/html\n\n")
    if not pils:
        ssw("ERROR: No pil specified...")
        return
    centerlimit = '' if center == '' else (" and source = '%s' " % (center, ))
    timelimit = ''
    if sdate != '':
        timelimit += " and entered >= '%s' " % (sdate, )
    if edate != '':
        timelimit += " and entered < '%s' " % (edate, )

    if pils[0][:3] == 'MTR':
        access = get_dbconn('iem', user='nobody')
        cursor = access.cursor()
        sql = """
            SELECT raw from current_log c JOIN stations t
            on (t.iemid = c.iemid)
            WHERE raw != '' and id = '%s' ORDER by valid DESC LIMIT %s
            """ % (pils[0][3:].strip(), limit)
        cursor.execute(sql)
        for row in cursor:
            if fmt == 'html':
                ssw("<pre>\n")
            else:
                ssw("\001\n")
            ssw(row[0].replace("\r\r\n", "\n"))
            if fmt == 'html':
                ssw("</pre>\n")
            else:
                ssw("\003\n")
        if cursor.rowcount == 0:
            ssw("ERROR: METAR lookup for %s failed" % (
                                                pils[0][3:].strip(), ))
        return

    try:
        mydb = get_dbconn('afos', user='nobody')
    except Exception as _exp:  # noqa
        ssw('Error Connecting to Database, please try again!\n')
        return

    cursor = mydb.cursor()

    if len(pils) == 1:
        pillimit = " pil = '%s' " % (pils[0], )
        if len(pils[0].strip()) == 3:
            pillimit = " substr(pil, 1, 3) = '%s' " % (pils[0].strip(), )
    else:
        pillimit = " pil in %s" % (tuple(pils), )
    ttlimit = ''
    if len(ttaaii) == 6:
        ttlimit = " and wmo = '%s' " % (ttaaii, )

    # Do optimized query first, see if we can get our limit right away
    sql = """
        SELECT data, pil,
        to_char(entered at time zone 'UTC', 'YYYYMMDDHH24MI') as ts
        from products WHERE %s
        and entered > now() - '31 days'::interval %s %s %s
        ORDER by entered DESC LIMIT %s""" % (pillimit, centerlimit,
                                             timelimit, ttlimit, limit)

    cursor.execute(sql)
    if cursor.rowcount != limit:
        sql = """
            SELECT data, pil,
            to_char(entered at time zone 'UTC', 'YYYYMMDDHH24MI') as ts
            from products WHERE %s %s %s %s
            ORDER by entered DESC LIMIT %s """ % (pillimit, centerlimit,
                                                  timelimit, ttlimit, limit)
        cursor.execute(sql)

    for row in cursor:
        if fmt == 'html':
            ssw((
                "<a href=\"/wx/afos/p.php?pil=%s&e=%s\">Permalink</a> "
                "for following product: "
                ) % (row[1], row[2]))
            ssw("<br /><pre>\n")
        else:
            ssw("\001\n")
        # Remove control characters from the product as we are including
        # them manually here...
        ssw((row[0]).replace(
            "\003", "").replace("\001\r\r\n", "").replace("\r\r\n", "\n"))
        if fmt == 'html':
            ssw("</pre><hr>\n")
        else:
            ssw("\n\003\n")

    if cursor.rowcount == 0:
        print("ERROR: Could not Find: %s" % (",".join(pils), ))


if __name__ == '__main__':
    main()


class TestRetrieve(unittest.TestCase):
    """some tests"""

    def test_pil_logic(self):
        """Make sure our pil logic works! """
        res = pil_logic("AFDDMX")
        assert len(res) == 1
        assert res[0] == 'AFDDMX'
        res = pil_logic("WAREWX")
        assert len(res) == 12
        res = pil_logic("STOIA,AFDDMX")
        assert res[0] == 'STOIA '
        assert res[1] == 'AFDDMX'
