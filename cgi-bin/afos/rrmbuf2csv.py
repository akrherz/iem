#!/usr/bin/env python
""" One off conversion of RRMBUF to CSV """
import psycopg2
import sys
import pytz

def run():
    """ Do Stuff """
    pgconn = psycopg2.connect(database='afos', host='iemdb', user='nobody')
    cursor = pgconn.cursor()
    
    cursor.execute("""
    SELECT data, entered from products where pil = 'RRMBUF' and 
    entered > ('TODAY'::date - '2 days'::interval) ORDER by entered DESC
    LIMIT 1
    """)
    
    sys.stdout.write("Content-type:text/plain\n\n")
    if cursor.rowcount == 0:
        sys.stdout.write("RRMBUF not found?!?!")
        return
    row = cursor.fetchone()
    sys.stdout.write("# based on IEM processing of RRMBUF dated: %s UTC\n"
                     % (row[1].astimezone(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M")))
    sys.stdout.write("id,timestamp,value,lat,lon,name\n")
    data = row[0].replace("\001", "")
    for line in data.split("\r\r\n"):
        if not line.startswith(".A"):
            continue
        tokens = line.split()
        sid = tokens[1]
        dv = "%s %s" % (tokens[2], tokens[4][2:6])
        val = tokens[5].split('"')[0]
        tokens2 = " ".join(tokens[5:]).split()
        #sys.stdout.write(line+"\n")
        sys.stdout.write("%9s,%s,%s,%s,%s,%s\n" % (sid, dv, val,
                                tokens2[0].split("=")[1], 
                                tokens2[1].split("=")[1],
                                " ".join(tokens2[2:]).split('"')[0]
                                ))

if __name__ == '__main__':
    run()