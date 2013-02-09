"""
 This script downloads the METAR data provided by wunderground, another script
 than compares it with my current archive and that provided by NSSL to see 
 if there are any differences.

Arguments
    python wunder_ingest.py --network=IA_ASOS 1978 1979
    python wunder_ingest.py --station=AMW 1978 1979

"""
import urllib2
import cookielib
import datetime
import time
import sys
import os
import pytz
from optparse import OptionParser
from metar import Metar
import iemdb
ASOS = iemdb.connect('asos')
acursor = ASOS.cursor()

class OB(object):
    station = None
    valid = None
    tmpf = None
    dwpf = None
    drct = None
    sknt = None
    alti = None
    gust = None
    vsby = None
    skyc1 = None
    skyc2 = None
    skyc3 = None
    skyc4 = None
    skyl1 = None
    skyl2 = None
    skyl3 = None
    metar = None
    skyl4 = None
    p03i = None 
    p06i = None
    p24i = None
    max_tmpf_6hr = None 
    min_tmpf_6hr = None 
    max_tmpf_24hr = None 
    min_tmpf_24hr = None
    mslp = None
    p01i = None 
    presentwx = None

def get_job_list():
    """ Figure out the days and stations we need to get """
    days = []
    stations = []
    
    parser = OptionParser()
    parser.add_option("-n", "--network", dest="network",
                  help="IEM network", metavar="NETWORK")
    parser.add_option("-s", "--station", dest="station",
                  help="IEM station", metavar="STATION")
    (options, args) = parser.parse_args()
    now = datetime.date(int(args[0]),1,1)
    ets = datetime.date(int(args[1]),1,1)
    while now < ets:
        days.append( now )
        now += datetime.timedelta(days=1)
    if options.network is not None:
        sql = """SELECT id from stations where network = %s ORDER by id ASC"""
        acursor.execute(sql, (options.network,) )
        for row in acursor:
            stations.append( row[0] )
    else:
        stations.append( options.station )
        

    return stations, days

def workflow():
    """ Do some work """
    stations, days = get_job_list()

    # Set the show metar option
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.open("http://www.wunderground.com/cgi-bin/findweather/getForecast?setpref=SHOWMETAR&value=1").read()

    # Iterate 
    for station in stations:
        clear_data(station, days[0], days[-1])
        total = 0
        for day in days:
            (processed, usedcache) = doit(opener, station, day)
            total += processed
            ASOS.commit()
            if not usedcache:
                time.sleep(0.5)
        print "%s processed %s entries" % (station, total)
            
def clear_data(station, sts, ets):
    acursor.execute("""DELETE from alldata WHERE station = %s and
    valid BETWEEN %s and %s""", (station, sts, 
                                 (ets + datetime.timedelta(days=1))))
    ASOS.commit()

def doit(opener, station, now):
    """ Fetch! """
    usedcache = False
    processed = 0
    
    if len(station) == 3:
        faa = "K%s" % (station,)
    else:
        faa = station
        
    mydir = "/mesonet/ARCHIVE/wunder/cache/%s/%s/" % (station, now.year)
    if not os.path.isdir(mydir):
        os.makedirs(mydir)
  
    fn = "%s%s.txt" % (mydir, now.strftime("%Y%m%d"), )
    if os.path.isfile(fn):
        usedcache = True
        data = open(fn).read()
        if len(data) < 140:
            usedcache = False
    if not usedcache:
        url = "http://www.wunderground.com/history/airport/%s/%s/%-i/%-i/DailyHistory.html?req_city=NA&req_state=NA&req_statename=NA&format=1" % (faa, now.year, now.month, now.day)
        try:
            data = opener.open(url).read()
        except KeyboardInterrupt:
            sys.exit()
        except:
            print "Download Fail STID: %s NOW: %s" % (station, now)
            return 0, False

    # Save raw data, since I am an idiot have of the time
    o = open(fn, 'w')
    o.write(data)
    o.close()
  
    lines = data.split("\n")
    headers = None
    for line in lines: 
        line = line.replace("<br />", "").replace("\xff", "")
        if line.strip() == "":
            continue
        tokens = line.split(",")
        if len(tokens) < 3:
            continue
        if headers is None:
            headers = {}
            for i in range(len(tokens)):
                headers[ tokens[i] ] = i
            continue
  
        if headers.has_key("FullMetar"):
            mstr = (tokens[headers["FullMetar"]]).strip().replace("'",
                                "").replace("SPECI ","").replace("METAR ","")
            ob = process_metar(mstr, now)
            if ob is None:
                continue

            sql = """INSERT into t"""+ `ob.valid.year` +""" (station, valid, 
            tmpf, dwpf, vsby, drct, sknt, gust, p01i, alti, skyc1, skyc2, 
            skyc3, skyc4, skyl1, skyl2, skyl3, skyl4, metar, mslp, presentwx,
            p03i, p06i, p24i, max_tmpf_6hr, max_tmpf_24hr, min_tmpf_6hr,
            min_tmpf_24hr) 
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, 
            %s, %s, %s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)""" 
            args = (station, ob.valid, ob.tmpf, ob.dwpf, ob.vsby, ob.drct,
                    ob.sknt, ob.gust, ob.p01i, ob.alti, ob.skyc1, ob.skyc2,
                    ob.skyc3, ob.skyc4, ob.skyl1, ob.skyl2, ob.skyl3,
                    ob.skyl4, ob.metar, ob.mslp, ob.presentwx, ob.p03i,
                    ob.p06i, ob.p24i, ob.max_tmpf_6hr, ob.max_tmpf_24hr,
                    ob.min_tmpf_6hr, ob.min_tmpf_24hr) 

            acursor.execute(sql, args)
            processed += 1

    return processed, usedcache

            
def process_metar(mstr, now):
    try:
        mtr = Metar.Metar(mstr, now.month, now.year)
    except:
        return None
    if mtr is None or mtr.time is None:
        return None
    
    ob = OB()
    ob.metar = mstr
    
    gts = datetime.datetime( mtr.time.year, mtr.time.month, 
                mtr.time.day, mtr.time.hour, mtr.time.minute)
    gts = gts.replace(tzinfo=pytz.timezone("UTC"))
    # When processing data on the last day of the month, we get GMT times
    # for the first of this month
    if gts.day == 1 and now.day > 10:
        tm = now + datetime.timedelta(days=1)
        gts = gts.replace(year=tm.year, month=tm.month, day=tm.day)
      
    ob.valid = gts
      
    if mtr.temp:
        ob.tmpf = mtr.temp.value("F")
    if (mtr.dewpt):
        ob.dwpf = mtr.dewpt.value("F")

    if mtr.wind_speed:
        ob.sknt = mtr.wind_speed.value("KT")
    if mtr.wind_gust:
        ob.gust = mtr.wind_gust.value("KT")

    if mtr.wind_dir and mtr.wind_dir.value() != "VRB":
        ob.drct = mtr.wind_dir.value()

    if mtr.vis:
        ob.vsby = mtr.vis.value("SM")

    if mtr.press:
        ob.alti = mtr.press.value("IN")
      
    if mtr.press_sea_level:
        ob.mslp = mtr.press_sea_level.value("MB")

    if mtr.precip_1hr:
        ob.p01i = mtr.precip_1hr.value("IN")

    # Do something with sky coverage
    for i in range(len(mtr.sky)):
        (c,h,b) = mtr.sky[i]
        setattr(ob, 'skyc%s' % (i+1), c)
        if h is not None:
            setattr(ob, 'skyl%s' % (i+1), h.value("FT"))

    if mtr.max_temp_6hr:
        ob.max_tmpf_6hr = mtr.max_temp_6hr.value("F")
    if mtr.min_temp_6hr:
        ob.min_tmpf_6hr = mtr.min_temp_6hr.value("F")
    if mtr.max_temp_24hr:
        ob.max_tmpf_24hr = mtr.max_temp_24hr.value("F")
    if mtr.min_temp_24hr: 
        ob.min_tmpf_6hr = mtr.min_temp_24hr.value("F")
    if mtr.precip_3hr:
        ob.p03i = mtr.precip_3hr.value("IN")
    if mtr.precip_6hr:
        ob.p06i = mtr.precip_6hr.value("IN")
    if mtr.precip_24hr:
        ob.p24i = mtr.precip_24hr.value("IN")

    # Presentwx
    if mtr.weather:
        pwx = []
        for x in mtr.weather:
            pwx.append( ("").join([a for a in x if a is not None]) )
        ob.presentwx = (",".join(pwx))[:24]
        
    return ob


if __name__ == "__main__":
    print 'Starting up...'
    workflow()
    ASOS.commit()
    ASOS.close()
    print 'Done!'