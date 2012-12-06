"""
Ingest Atmospheric Structure Instrument Data from Dr Takle, 
this comes via email!
network: ISUASI
Sites: ISU4003 42.1527 -93.375 329m
       ISU4002 42.1921 -93.357 352m

 1 48.5m Wind Speed m/s 
 2 48.5m Wind Speed m/s
 3 32m   Wind Speed m/s
 4 32m   Wind Speed m/s
 5 10m   Wind Speed m/s
 6 10m   Wind Speed m/s
 7 47m   Wind Dir   deg
 8 40m   Wind Dir   deg
 9 10m   Wind Dir   deg
10  3m   Air Temp   C
11 48.5m Air Temp   C
12 48.5m Barometer  mb

"""
import logging
import logging.handlers
log = logging.getLogger('ASI_INGEST')
log.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
log.addHandler(handler)

import sys
import mx.DateTime
import email.parser
import psycopg2
import time
OTHER = psycopg2.connect('dbname=other host=127.0.0.1 user=akrherz')
ocursor = OTHER.cursor()

SQL = """INSERT into asi_data values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
def process(fp):
    """ Process some raw data, please """
    skips = 0
    count = 0
    for line in open(fp):
        tokens = line.split("\t")
        if line.find("Site #") == 0:
            sid = "ISU%s" % (line[6:].strip(),)
        if len(tokens) != 49 or tokens[1] == 'CH1Avg':
            continue
        # We have data!
        ts = mx.DateTime.strptime(tokens[0], '%m/%d/%Y %H:%M:%S')
        tokens.insert(0, sid)
        tokens[1] = ts.strftime("%Y-%m-%d %H:%M:%S-06")
        ocursor.execute("""SELECT * from asi_data WHERE station = %s
        and valid = %s""", (sid, tokens[1]))
        if ocursor.rowcount == 0:
            ocursor.execute(SQL, tokens)
            count += 1
        else:
            skips += 1

    log.info('%s New Obs: %s Skips: %s' % (fp, count, skips))

def email_process():
    msg = email.parser.Parser().parse(sys.stdin)
    for part in msg.walk():
        if part.get_filename() != None:
            fp = mx.DateTime.now().strftime("/home/colo/asi%Y%m%d%H%M%S.txt")
            o = open(fp, 'a')
            o.write( part.get_payload() )
            o.close()
            
            try:
                process( fp )
                time.sleep(2)
            except:
                # TODO
                pass

if __name__ == '__main__':
    if len(sys.argv) == 1:
        email_process()
    else:
        process(sys.argv[1])

ocursor.close()
OTHER.commit()
OTHER.close()