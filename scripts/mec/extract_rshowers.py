import pytz
import datetime
from pyiem.util import get_dbconn
pgconn = get_dbconn('mec', user='mesonet')
cursor = pgconn.cursor()

dates = """06-02-2008 00z - 06-07-2008 06z
06-09-2008 00z - 06-14-2008 06z
06-23-2008 00z - 06-25-2008 06z
07-04-2008 00z - 07-06-2008 06z
08-15-2008 00z - 08-23-2008 06z
02-19-2009 00z - 02-25-2009 06z
03-02-2009 00z - 03-07-2009 06z
03-28-2009 00z - 04-03-2009 06z"""
dates = """06-14-2008 00z - 06-17-2008 00z
06-21-2008 00z - 07-04-2008 00z
07-10-2008 00z - 07-16-2008 00z
08-02-2008 00z - 08-05-2008 00z
08-27-2008 00z - 08-28-2008 00z
03-16-2008 00z - 03-18-2008 00z"""
dates = """08-25-2008 00z - 08-29-2008 00z
03-03-2009 00z - 03-07-2009 00z"""

def c(val):
    if val is None:
        return 'M'
    return val

for line in dates.split("\n"):
    tokens = line.split(" - ")
    sts = datetime.datetime.strptime(tokens[0][:12], '%m-%d-%Y %H')
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    ets = datetime.datetime.strptime(tokens[1][:12], '%m-%d-%Y %H')
    ets = ets.replace(tzinfo=pytz.timezone("UTC"))
    output = open('extract/%s-%s.txt' % (sts.strftime("%Y%m%d%H%M"),
                                         ets.strftime("%Y%m%d%H%M")), 'w')
    output.write("utcvalid,avg_power,avg_windspeed,stddev_windspeed,count,avg_yaw\n")
    cursor.execute("""
      select valid, avg(power), avg(windspeed), stddev(windspeed),
      count(*), avg(yaw2) from sampled_data 
      WHERE valid >= %s and valid < %s 
      and extract(minute from valid)::int %% 10 = 0 and power is not null
      and windspeed is not null GROUP by valid ORDER by valid ASC
    """, (sts, ets))
    print sts, ets, cursor.rowcount
    for row in cursor:
        ts = row[0].astimezone(pytz.timezone("UTC"))
        output.write("%s,%s,%s,%s,%s,%s\n"  % ( 
           ts.strftime("%Y-%m-%d %H:%M:%S"), 
           c(row[1]), c(row[2]), c(row[3]), row[4], c(row[5]) ))

    output.close()
