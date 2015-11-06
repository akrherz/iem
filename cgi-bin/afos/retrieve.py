#!/usr/bin/env python

import psycopg2
import cgi
import sys
import unittest


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
    sys.stdout.write("X-Content-Type-Options: nosniff\n")
    sys.stdout.write("Content-type: text/plain\n\n")
    form = cgi.FieldStorage()
    pils = pil_logic(form.getfirst('pil', ''))
    limit = int(form.getfirst('limit', 1))
    center = form.getfirst('center', '')[:4]
    sdate = form.getfirst('sdate', '')[:10]
    edate = form.getfirst('edate', '')[:10]
    fmt = form.getfirst('fmt', 'text')
    if len(pils) == 0:
        sys.stdout.write("ERROR: No pil specified...")
        return
    centerlimit = '' if center == '' else (" and source = '%s' " % (center, ))
    timelimit = ''
    if sdate != '' and edate != '':
        timelimit = (" and entered >= '%s' and entered < '%s' "
                     ) % (sdate, edate)

    if pils[0][:3] == 'MTR':
        access = psycopg2.connect(database='iem', host='iemdb', user='nobody')
        cursor = access.cursor()
        sql = """
            SELECT raw from current_log c JOIN stations t
            on (t.iemid = c.iemid)
            WHERE raw != '' and id = '%s' ORDER by valid DESC LIMIT %s
            """ % (pils[0][3:].strip(), limit)
        cursor.execute(sql)
        for row in cursor:
            sys.stdout.write("\001\n")
            sys.stdout.write(row[0].replace("\r\r\n", "\n"))
            sys.stdout.write("\n\003")
        if cursor.rowcount == 0:
            sys.stdout.write("ERROR: METAR lookup for %s failed" % (
                                                pils[0][3:].strip(), ))
        return

    try:
        mydb = psycopg2.connect(database='afos', host='iemdb', user='nobody')
    except:
        print 'Error Connecting to Database, please try again!'
        return

    cursor = mydb.cursor()

    if len(pils) == 1:
        pillimit = " pil = '%s' " % (pils[0], )
    else:
        pillimit = " pil in %s" % (tuple(pils), )

    # Do optimized query first, see if we can get our limit right away
    sql = """
        SELECT data from products WHERE %s
        and entered > now() - '2 days'::interval %s %s
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


class tester(unittest.TestCase):

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
