'''
 Generate and email a report to the IASS folks with summarized IEM estimated
 COOP data included...
'''
import sys
import psycopg2
import psycopg2.extras
import network
import cStringIO
import datetime
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

nt = network.Table("IACLIMATE")

districts = [
'North West',
'North Central',
'North East',
'West Central',
'Central',
'East Central',
'South West',
'South Central',
'South East',             
]

stids = [
['IA2724', 'IA4735', 'IA7844', 'IA5493'],
['IA0923', 'IA3980', 'IA5230', 'IA6305'],
['IA2110', 'IA2364', 'IA3517', 'IA2864'],
['IA1233', 'IA1277', 'IA3509', 'IA3632', 'IA4228', 'IA4894', 'IA7161', 
    'IA7312', 'IA7708'],
['IA0200', 'IA2203', 'IA3487', 'IA5198', 'IA5992', 'IA6566', 'IA8296'],
['IA1319', 'IA4705', 'IA4101', 'IA8266', 'IA5131', 'IA5837'],
['IA0364', 'IA1533', 'IA3290', 'IA6940', 'IA7669'],
['IA0112', 'IA5769', 'IA1394', 'IA4063', 'IA4585'],
['IA0753', 'IA1063', 'IA6389', 'IA8688']         
]

def compute_weekly(fp, sts, ets):
    ''' Compute the weekly stats we need '''
    coop = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = coop.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Max daily high
    # min daily high
    # average temperature 
    # departure from normal for average temp
    # Total precip 
    # precip departure from normal
    # since 1 april precip
    # since 1 april departure
    # since 1 april GDD50
    # since 1 april departure
    sday = sts.strftime("%m%d")
    eday = ets.strftime("%m%d")
    cursor.execute("""
    WITH obs as (
        SELECT station, 
        max(high) as hi,
        min(low)  as lo,
        avg((high+low)/2.) as avg,
        sum(precip) as total_p
        FROM alldata_ia WHERE day >= %s and day <= %s 
        GROUP by station
    ), april_obs as (
        SELECT station, 
        sum(precip) as p, 
        sum(gddxx(50,86,high,low)) as gdd
        from alldata_ia WHERE year = %s and month > 3
        GROUP by station
    ), climo as (
        SELECT station,
        avg((high+low)/2.) as avg,
        sum(precip) as avg_p
        from climate51 
        WHERE to_char(valid, 'mmdd') >= %s and to_char(valid, 'mmdd') <= %s
        GROUP by station
    ), april_climo as (
        SELECT station,
        sum(precip) as avg_p,
        sum(gdd50) as avg_gdd
        from climate51 WHERE extract(month from valid) > 3
        and to_char(valid, 'mmdd') < %s
        GROUP by station
    )  SELECT obs.station,
    obs.hi,
    obs.lo,
    obs.avg,
    (obs.avg - climo.avg) as temp_dfn,
    obs.total_p,
    (obs.total_p - climo.avg_p) as precip_dfn,
    april_obs.p as april_p,
    (april_obs.p - april_climo.avg_p) as april_p_dfn,
    april_obs.gdd as april_gdd,
    (april_obs.gdd - april_climo.avg_gdd) as april_gdd_dfn
    from obs JOIN climo on (obs.station = climo.station)
    JOIN april_obs on (obs.station = april_obs.station)
    JOIN april_climo on (april_climo.station  = obs.station)
""", (sts, ets, sts.year, sday, eday, eday))
    data = {}
    for row in cursor:
        data[row['station']] = row
        
    for district, sector in zip(districts, stids):
        fp.write("%s District\n" % (district,))
        for sid in sector:
            fp.write("%-15.15s %3s %3s %3.0f %3.0f  %5.2f  %5.2f   %5.2f %6.2f %7.0f %5.0f\n" % (nt.sts[sid]['name'], 
                                            data[sid]['hi'], 
                                            data[sid]['lo'], data[sid]['avg'],
                                            data[sid]['temp_dfn'],
                                            data[sid]['total_p'],
                                            data[sid]['precip_dfn'],
                                            data[sid]['april_p'],
                                            data[sid]['april_p_dfn'],
                                            data[sid]['april_gdd'],
                                            data[sid]['april_gdd_dfn']))


def compute_monthly(fp, year, month):
    ''' Compute the monthly data we need to compute '''
    coop = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = coop.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Max daily high
    # min daily high
    # average temperature 
    # departure from normal for average temp
    # Total precip 
    # precip departure from normal
    # days with measurable precip
    # heating degree days
    # heating degree day departure
    # days with temp below 32
    # days with temp below 28
    
    cursor.execute("""
    WITH obs as (
        SELECT station, 
        max(high) as hi,
        min(low)  as lo,
        avg((high+low)/2.) as avg,
        sum(precip) as total_p,
        sum(case when precip >= 0.01 then 1 else 0 end) as days,
        sum(hdd65(high,low)) as hdd,
        sum(case when low <= 32 then 1 else 0 end) as days32,
        sum(case when low <= 28 then 1 else 0 end) as days28
        FROM alldata_ia WHERE year = %s and month = %s
        GROUP by station
    ), climo as (
        SELECT station,
        avg((high+low)/2.) as avg,
        sum(precip) as avg_p,
        sum(hdd65) as avg_hdd
        from climate51 WHERE extract(month from valid) = %s
        GROUP by station
    )  SELECT obs.station,
    obs.hi,
    obs.lo,
    obs.avg,
    (obs.avg - climo.avg) as temp_dfn,
    obs.total_p,
    (obs.total_p - climo.avg_p) as precip_dfn,
    obs.days,
    obs.hdd,
    (obs.hdd - climo.avg_hdd) as hdd_dfn,
    obs.days32,
    obs.days28
    from obs JOIN climo on (obs.station = climo.station)
""", (year, month, month))
    data = {}
    for row in cursor:
        data[row['station']] = row
        
    for district, sector in zip(districts, stids):
        fp.write("%s District\n" % (district,))
        for sid in sector:
            fp.write("%-15.15s %3s %3s %3.0f %3.0f  %5.2f  %5.2f   %2s %5.0f %5.0f %3s  %3s\n" % (nt.sts[sid]['name'], 
                                            data[sid]['hi'], 
                                            data[sid]['lo'], data[sid]['avg'],
                                            data[sid]['temp_dfn'],
                                            data[sid]['total_p'],
                                            data[sid]['precip_dfn'],
                                            data[sid]['days'],
                                            data[sid]['hdd'] or 0,
                                            data[sid]['hdd_dfn'] or 0,
                                            data[sid]['days32'],
                                            data[sid]['days28']))
    

def monthly_header(fp, sts, ets):
    ''' Write the monthly header information '''
    fp.write("""Weather Summary For Iowa Agricultural Statistics Service
Prepared By Iowa Environmental Mesonet
 
For the Period:    %s 
            To:    %s 
 
                                                               DAYS DAYS
                      AIR                                       OF   OF 
                  TEMPERATURE      PRECIPITATION     HDD   HDD  32   28
STATION          HI  LO AVG DFN  TOTAL    DFN DAYS   TOT   DFN COLD COLD
-------          --  --  --  --  -----   ----   --   ---   ---  --   -- 
""" % (sts.strftime("%A %B %d, %Y"), ets.strftime("%A %B %d, %Y")))

def weekly_header(fp, sts, ets):
    ''' Write the header information '''
    fp.write("""Weather Summary For Iowa Agricultural Statistics Service
Prepared By Iowa Environmental Mesonet

For the Period:     %s
            To:     %s


                         CURRENT WEEK           SINCE APR 1    SINCE APR 1
                   TEMPERATURE  PRECIPITATION  PRECIPITATION  GDD BASE 50F
                   -----------  -------------  -------------  ------------
STATION          HI  LO AVG DFN  TOTAL    DFN   TOTAL    DFN   TOTAL   DFN
-------          --  --  --  --  -----   ----   -----   ----   -----  ----
""" % (sts.strftime("%A %B %d, %Y"), ets.strftime("%A %B %d, %Y")))
    
def email_report(report, subject):
    ''' Actually do the emailing stuff '''
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = 'mesonet@mesonet.agron.iastate.edu'
    msg['Cc'] = 'akrherz@iastate.edu'
    msg['To'] = 'NASSRFOUMR@nass.usda.gov' if len(sys.argv) != 5 else 'akrherz@localhost'
    msg.preamble = 'Report'

    fn = "iem.txt" 

    b = MIMEBase('Text', 'Plain')
    report.seek(0)
    b.set_payload(report.read())
    encoders.encode_base64(b)
    b.add_header('Content-Disposition', 'attachment; filename="%s"' % (fn))
    msg.attach(b)

    # Send the email via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()

    
if __name__ == '__main__':
    ''' If we are in Nov,Dec,Jan,Feb,Mar -> do monthly report 
     otherwise, do the weekly 
     This script is run each Monday or the first of the month 
     from RUN_2AM script
    '''
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    rtype = sys.argv[1]
    if rtype == "monthly" and yesterday.month in (11,12,1,2,3):
        if len(sys.argv) >= 4:
            sts = datetime.date( int(sys.argv[2]), int(sys.argv[3]), 1)
            ets = sts + datetime.timedelta(days=35)
            ets = ets.replace(day=1)
        else:
            sts = yesterday.replace(day=1) 
            ets = yesterday
        report = cStringIO.StringIO()
        monthly_header(report, sts, ets)
        compute_monthly(report, sts.year, sts.month)
        email_report(report, "IEM Monthly Data Report")
    if rtype == "daily" and today.month in range(4,11):        
        sts = today - datetime.timedelta(days=7)
        ets = yesterday
        report = cStringIO.StringIO()
        weekly_header(report, sts, ets)
        compute_weekly(report, sts, ets)    
        email_report(report, "IEM Weekly Data Report")
