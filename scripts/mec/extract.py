import pytz
import datetime
from pyiem.util import get_dbconn
pgconn = get_dbconn('mec', user='mesonet')
cursor = pgconn.cursor()

def c(val):
    if val is None:
        return 'M'
    return val

for line in open('dates.txt'):
    tokens = line.split(" - ")
    sts = datetime.datetime.strptime(tokens[0][:10], '%m-%d-%Y')
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    ets = datetime.datetime.strptime(tokens[1][:10], '%m-%d-%Y')
    ets = ets.replace(tzinfo=pytz.timezone("UTC"))
    output = open('extract/%s-%s.txt' % (sts.strftime("%Y%m%d%H%M"),
                                         ets.strftime("%Y%m%d%H%M")), 'w')
    output.write("turbineid,utcvalid,power,pitch,yaw,windspeed\n")
    cursor.execute("""
      select turbineid, valid, power, pitch, yaw, windspeed from turbine_data 
      WHERE valid >= %s and valid < %s ORDER by valid ASC
    """, (sts, ets))
    print sts, ets, cursor.rowcount
    for row in cursor:
        ts = row[1].astimezone(pytz.timezone("UTC"))
        output.write("%s,%s,%s,%s,%s,%s\n"  % (row[0], 
           ts.strftime("%Y-%m-%d %H:%M:%S"), 
           c(row[2]), c(row[3]), c(row[4]), c(row[5])))

    output.close()
