#!/usr/bin/env python
"""give me some AFOS data please"""
from __future__ import print_function
import cgi
import sys
import unittest

from pyiem.util import get_dbconn


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
    limit = int(form.getfirst('limit', 1))
    center = form.getfirst('center', '')[:4]
    sdate = form.getfirst('sdate', '')[:10]
    edate = form.getfirst('edate', '')[:10]
    fmt = form.getfirst('fmt', 'text')
    sys.stdout.write("X-Content-Type-Options: nosniff\n")
    if form.getfirst('dl') == "1":
        sys.stdout.write("Content-type: application/octet-stream\n")
        sys.stdout.write(("Content-Disposition: "
                          "attachment; filename=afos.txt\n\n"))
    else:
        if fmt == 'text':
            sys.stdout.write("Content-type: text/plain\n\n")
        elif fmt == 'html':
            sys.stdout.write("Content-type: text/html\n\n")
    if not pils:
        sys.stdout.write("ERROR: No pil specified...")
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
                sys.stdout.write("<pre>\n")
            else:
                sys.stdout.write("\001\n")
            sys.stdout.write(row[0].replace("\r\r\n", "\n"))
            if fmt == 'html':
                sys.stdout.write("</pre>\n")
            else:
                sys.stdout.write("\003\n")
        if cursor.rowcount == 0:
            sys.stdout.write("ERROR: METAR lookup for %s failed" % (
                                                pils[0][3:].strip(), ))
        return

    try:
        mydb = get_dbconn('afos', user='nobody')
    except Exception as exp:
        print('Error Connecting to Database, please try again!')
        return

    cursor = mydb.cursor()

    if len(pils) == 1:
        pillimit = " pil = '%s' " % (pils[0], )
    else:
        pillimit = " pil in %s" % (tuple(pils), )

    # Do optimized query first, see if we can get our limit right away
    sql = """
        SELECT data from products WHERE %s
        and entered > now() - '31 days'::interval %s %s
        ORDER by entered DESC LIMIT %s""" % (pillimit, centerlimit,
                                             timelimit, limit)

    cursor.execute(sql)
    if cursor.rowcount != limit:
        sql = """
            SELECT data from products WHERE %s %s %s
            ORDER by entered DESC LIMIT %s """ % (pillimit, centerlimit,
                                                  timelimit, limit)
        cursor.execute(sql)

    for row in cursor:
        if fmt == 'html':
            sys.stdout.write("<pre>\n")
        else:
            sys.stdout.write("\001\n")
        # Remove control characters from the product as we are including
        # them manually here...
        sys.stdout.write((row[0]).replace(
            "\003", "").replace("\001\r\r\n", "").replace("\r\r\n", "\n"))
        if fmt == 'html':
            sys.stdout.write("</pre>\n")
        else:
            sys.stdout.write("\n\003\n")

    if cursor.rowcount == 0:
        print("ERROR: Could not Find: %s" % (",".join(pils), ))


if __name__ == '__main__':
    main()


class TestRetrieve(unittest.TestCase):
    """some tests"""

    def test_pil_logic(self):
        """Make sure our pil logic works! """
        res = pil_logic("AFDDMX")
        self.assertEquals(len(res), 1)
        self.assertEquals(res[0], 'AFDDMX')
        res = pil_logic("WAREWX")
        self.assertEquals(len(res), 12)
        res = pil_logic("STOIA,AFDDMX")
        self.assertEquals(res[0], 'STOIA ')
        self.assertEquals(res[1], 'AFDDMX')
