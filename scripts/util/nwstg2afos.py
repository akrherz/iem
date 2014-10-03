"""
 Ingest the NWSTG text files into the AFOS IEM database
"""
import psycopg2
import datetime
import sys
import tarfile
import subprocess
import pytz
import re
import os

BAD_CHARS = "[^\na-zA-Z0-9:\(\)\%\.,\s\*\-\?\|/><&$=\+\@]"

PGCONN = psycopg2.connect(database='afos', host='iemdb')

def find_awipsid(data):
    """ Attempt to guess the AWIPSID """
    tokens = re.findall("[0-9]{6}\s+([A-Z][A-Z][A-Z][A-Z0-9]{1,3})", data)
    if len(tokens) == 0:
        return None
    return tokens[0]

def do(ts):
    """ Process this timestamp """
    cursor = PGCONN.cursor()

    fn = ts.strftime("/mnt/mesonet2/data/nwstg/NWSTG_%Y%m%d.tar.Z")
    if not os.path.isfile(fn):
        print("MISSING FILE: %s" % (fn,))
        return
    subprocess.call("uncompress %s" % (fn,), shell=True)
    tar = tarfile.open(fn[:-2], 'r')
    for member in tar.getmembers():
        f = tar.extractfile(member)
        tar2 = tarfile.open(fileobj=f, mode='r')
        for member2 in tar2.getmembers():
            f2 = tar2.extractfile(member2)
            if not f2.name.startswith("TEXT_"):
                continue
            content = (re.sub(BAD_CHARS, "", f2.read())).replace("\r\r", "")
            awipsid = find_awipsid(content)
            if (awipsid is not None and 
                (awipsid.startswith("RR") or awipsid.startswith("MTR")
                 or awipsid in ["TSTNCF", "WTSNCF"])):
                print 'Skip', f2.name, awipsid
                continue
            parts = f2.name.strip().split("_")
            ttaaii = parts[1]
            source = parts[2]
            if source[0] not in ['K', 'P']:
                continue
            if source in ['KWBC', 'KWAL']:
                continue
            if parts[4] == '2400':
                parts[4] = '2359'
            try:
                valid = datetime.datetime.strptime(parts[3]+"_"+parts[4], 
                                               '%Y%m%d_%H%M')
            except:
                print 'Invalid timestamp', f2.name
                continue
            
            if valid.year != ts.year:
                print 'Invalid timestamp, year mismatch'
                continue
            
            valid = valid.replace(tzinfo=pytz.timezone("UTC"))
                
            table = "products_%s_%s" % (valid.year, 
                                        "0712" if valid.month > 6 else "0106")
            
            print f2.name, ttaaii, valid.strftime("%Y%m%d%H%M"), source, awipsid, table
            cursor.execute("""INSERT into """+table+"""
            (data, pil, entered, source, wmo) values (%s,%s,%s,%s,%s)""",
            (content, awipsid, valid, source, ttaaii))
            
    cursor.close()
    PGCONN.commit()
    subprocess.call("compress %s" % (fn[:-2],), shell=True)
    
def main():
    """ Go Main Go """
    sts = datetime.datetime( int(sys.argv[1]), int(sys.argv[2]),
                             int(sys.argv[3]))
    ets = datetime.datetime( int(sys.argv[4]), int(sys.argv[5]),
                             int(sys.argv[6]))
    now = sts
    while now <= ets:
        do(now)
        now += datetime.timedelta(days=1)


if __name__ == '__main__':
    # do something
    main()