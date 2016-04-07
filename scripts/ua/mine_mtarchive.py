import subprocess
import datetime
import pytz
import urllib2
from ingest_from_rucsoundings import RAOB
import psycopg2

POSTGIS = psycopg2.connect(database='postgis', host='iemdb')

def conv( raw):
    if float(raw) < -9998:
        return None
    return float(raw) 

sts = datetime.datetime(1989, 9, 25)
ets = datetime.datetime(1989, 9, 26)
interval = datetime.timedelta(days=1)
now = sts
while now < ets:
    print now
    uri = now.strftime("http://mtarchive.geol.iastate.edu/%Y/%m/%d/gempak/upperair/%Y%m%d_upa.gem")
    try:
        data = urllib2.urlopen(uri).read()
        o = open('data.gem', 'wb')
        o.write(data)
        o.close()
    except Exception, exp:
        print exp
        now += interval
        continue

    o = open('fn', 'w')
    o.write("""
SNFILE=data.gem
AREA=DSET
DATTIM=ALL
SNPARM=TMPC;DWPC;HGHT;DRCT;SKNT
LEVELS=ALL
 VCOORD   = PRES
 OUTPUT   = T
 MRGDAT   = YES
run

exit
""")
    o.close()
    p = subprocess.Popen("snlist < fn", stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    data = p.stdout.read()
    myraob = None
    for line in data.split("\n"):
        if line.strip()[:4] == 'STID':

            if myraob is not None:
                print str(myraob)
                txn = POSTGIS.cursor()
                myraob.database_save(txn)
                txn.close()
                POSTGIS.commit()
                myraob = None
            tokens = line.strip().split()
            myraob = RAOB()
            myraob.station = tokens[2]
            valid = datetime.datetime.strptime("19"+tokens[-1], '%Y%m%d/%H%M')
            myraob.valid = valid.replace(tzinfo=pytz.timezone("UTC"))
        if line.find(".") > 0 and line.find("=") == -1 and line.find("PRES") == -1:
            tokens = line.strip().split()
            if len(tokens) < 6:
                continue
            myraob.profile.append({'levelcode': None,
                                'pressure': float(tokens[0]),
                                'height': conv(float(tokens[3])),
                                'tmpc': conv(float(tokens[1])),
                                'dwpc': conv(float(tokens[2])),
                                'drct': conv(float(tokens[4])),
                                'smps': myraob.conv_speed(tokens[5]),
                                'ts': None,
                                'bearing': None,
                                'range': None
                                })

    now += interval