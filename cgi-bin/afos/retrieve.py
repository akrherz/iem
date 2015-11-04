#!/usr/bin/env python

import psycopg2
import cgi
import sys


def main():
    """Process the request"""
    # Attempt to keep the file from downloading and just displaying in chrome
    sys.stdout.write("X-Content-Type-Options: nosniff\n")
    sys.stdout.write("Content-type: text/plain\n\n")
    form = cgi.FieldStorage()
    pil0 = form.getfirst('pil', '')[:6]
    limit = int(form.getfirst('limit', 1))
    center = form.getfirst('center', '')[:4]
    sdate = form.getfirst('sdate', '')[:10]
    edate = form.getfirst('edate', '')[:10]
    fmt = form.getfirst('fmt', 'text')
    if pil0 == '':
        sys.stdout.write("ERROR: No pil specified...")
        return
    centerlimit = '' if center == '' else (" and source = '%s' " % (center, ))
    timelimit = ''
    if sdate != '' and edate != '':
        timelimit = (" and entered >= '%s' and entered < '%s' "
                     ) % (sdate, edate)

    pils = pil0.split(",")
    myPils = []
    for pil in pils:
        if len(pil) < 3:
            print 'Invalid PIL, try again'
            return
        if pil[:3] == "WAR":
            for q in ['FLS', 'FFS', 'AWW', 'TOR', 'SVR', 'FFW', 'SVS',
                      'LSR', 'SPS', 'WSW', 'FFA', 'WCN']:
                pils.append('%s%s' % (q, pil[3:]))
            continue
        myPils.append("%6s" % (pil + "      ",))

    pilAR = "("
    for pil in myPils:
        pilAR += "'%s'," % (pil,)
    pilAR = pilAR[:-1] + ")"

    if myPils[0][:3] == 'MTR':
        access = psycopg2.connect(database='iem', host='iemdb', user='nobody')
        cursor = access.cursor()
        sql = """
            SELECT raw from current_log c JOIN stations t
            on (t.iemid = c.iemid)
            WHERE raw != '' and id = '%s' ORDER by valid DESC LIMIT %s
            """ % (myPils[0][3:].strip(), limit)
        cursor.execute(sql)
        for row in cursor:
            sys.stdout.write("\001\n")
            sys.stdout.write(row[0].replace("\r\r\n", "\n"))
            sys.stdout.write("\n\003")
        if cursor.rowcount == 0:
            sys.stdout.write("ERROR: METAR lookup for %s failed" % (
                                                myPils[0][3:].strip(), ))
        return

    try:
        mydb = psycopg2.connect(database='afos', host='iemdb', user='nobody')
    except:
        print 'Error Connecting to Database, please try again!'
        return

    cursor = mydb.cursor()

    # Do optimized query first, see if we can get our limit right away
    sql = """
        SELECT data from products WHERE pil IN """ + pilAR + """
        and entered > now() - '2 days'::interval %s %s
        ORDER by entered DESC LIMIT %s""" % (centerlimit, timelimit, limit)

    cursor.execute(sql)
    if cursor.rowcount != limit:
        sql = """
            SELECT data from products WHERE pil IN """ + pilAR + """ %s %s
            ORDER by entered DESC LIMIT %s """ % (centerlimit, timelimit,
                                                  limit)
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
        print "Could not Find: "+pil


if __name__ == '__main__':
    main()
