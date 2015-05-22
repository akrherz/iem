#!/usr/bin/env python

import psycopg2
import cgi
import sys


def main():
    ''' Go main Go '''
    sys.stdout.write("Content-type: text/plain; charset=""\n\n")
    form = cgi.FormContent()
    if "pil" in form:
        pil0 = form["pil"][0].upper()
    else:
        sys.stdout.write("ERROR: No pil specified...")
        return

    if "limit" in form:
        LIMIT = str(form["limit"][0])
    else:
        LIMIT = "1"

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
            """ % (myPils[0][3:].strip(), LIMIT)
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
        and entered > now() - '2 days'::interval
        ORDER by entered DESC LIMIT """+LIMIT

    cursor.execute(sql)
    if cursor.rowcount != int(LIMIT):
        sql = """
            SELECT data from products WHERE pil IN """ + pilAR + """
            ORDER by entered DESC LIMIT """+LIMIT
        cursor.execute(sql)

    for row in cursor:
        print "\001"
        print (row[0]).replace("\003",
                               "").replace("\001", "").replace("\r\r\n", "\n")
        print "\n\003"

    if cursor.rowcount == 0:
        print "Could not Find: "+pil


if __name__ == '__main__':
    main()
