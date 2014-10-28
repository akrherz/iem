"""
Dump what I have stored in the AFOS database to flat files
"""
import psycopg2
pgconn = psycopg2.connect(database='afos', host='iemdb', user='nobody')
cursor = pgconn.cursor()

import datetime
import subprocess

pils = "LSR|FWW|CFW|TCV|RFW|FFA|SVR|TOR|SVS|SMW|MWS|NPW|WCN|WSW|EWW|FLS|FLW|SPS|SEL|SWO|FFW"

def sanitize(data):
    """ Make sure we have the right control characters """
    if data.find("\001") == -1:
        data = "\001"+data
    if data.find("\003") == -1:
        data = data+"\003"
    return data

def do(date):
    """ Process a given UTC date """
    table = "products_%s_%s" % (date.year, "0712" if date.month > 6 else '0106')
    for pil in pils.split("|"):
        cursor.execute("""SELECT data from """+table+""" WHERE 
        entered >= '%s 00:00+00' and entered < '%s 00:00+00' and
        substr(pil,1,3) = '%s' ORDER by entered ASC""" % (
            date.strftime("%Y-%m-%d"),
            (date + datetime.timedelta(hours=36)).strftime("%Y-%m-%d"),
            pil))
        if cursor.rowcount == 0:
            continue
        print('%s %s %s' % (date, pil, cursor.rowcount))
        o = open('/tmp/afos.tmp', 'w')
        for row in cursor:
            o.write(sanitize(row[0]))
        o.close()
        
        cmd = "data a %s0000 bogus text/noaaport/%s_%s.txt txt" % (
                    date.strftime("%Y%m%d"), pil, date.strftime("%Y%m%d"))
        cmd = "/home/ldm/bin/pqinsert -p '%s' /tmp/afos.tmp" % (cmd,)
        subprocess.call(cmd, shell=True)
    
def main():
    sts = datetime.datetime(2000,1,1)
    ets = datetime.datetime(2006,8,4)
    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        do(now)
        now += interval
    
if __name__ == '__main__':
    # go
    main()