#!/usr/bin/env python
""" One off conversion of RRMBUF to CSV """
import psycopg2
import sys
import pytz

def do(cursor, wfo):

    cursor.execute("""
    SELECT data, entered from products where pil = 'RRM%s' and 
    entered > ('TODAY'::date - '2 days'::interval) ORDER by entered DESC
    LIMIT 1
    """ % (wfo,))
    
    if cursor.rowcount == 0:
        return "# RRM%s not found?!?!\n" % (wfo,), ""
    row = cursor.fetchone()

    meta = "# based on IEM processing of RRM%s dated: %s UTC\n" % (
                                wfo,
        row[1].astimezone(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M"))
    data = row[0].replace("\001", "")
    meat = ""
    for line in data.split("\r\r\n"):
        if not line.startswith(".A"):
            continue
        tokens = line.split()
        sid = tokens[1]
        dv = "%s %s" % (tokens[2], tokens[4][2:6])
        val = tokens[5].split('"')[0]
        tokens2 = " ".join(tokens[5:]).split()
        #sys.stdout.write(line+"\n")
        meat += "%9s,%s,%s,%s,%s,%s\n" % (sid, dv, val,
                                tokens2[0].split("=")[1], 
                                tokens2[1].split("=")[1],
                                " ".join(tokens2[2:]).split('"')[0]
                                )

    return meta, meat

def run():
    """ Do Stuff """
    pgconn = psycopg2.connect(database='afos', host='iemdb', user='nobody')
    cursor = pgconn.cursor()
    sys.stdout.write("Content-type:text/plain\n\n")
    m1 = ""
    m2 = ""
    for wfo in ['OKX', 'ALY', 'BTV', 'BUF']:
        meta, meat = do(cursor, wfo)
        m1 += meta
        m2 += meat

    sys.stdout.write(m1)
    sys.stdout.write("id,timestamp,value,lat,lon,name\n")
    sys.stdout.write(m2)

if __name__ == '__main__':
    run()