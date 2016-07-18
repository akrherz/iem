#!/usr/bin/env python
"""Placefile for NEXRAD l3 storm attributes

TODO suggestions:
> On another note, it might be nice to set thresholds for visibility when
> things get cluttered, such as ~420 for overall visibility so you can
> zoom out to max to drop the icons, and maybe a lower value (like 200)
> for storms that don't have either MDA, Hail, or TVS on them. This
> shouldn't take more than changing a few constants and maybe an
> if/assignment statement or two.

TODO:
Add storm tracks.


"""
import cgi
import sys
import math
import memcache
import pyproj
import numpy as np
import psycopg2.extras
from pyiem.datatypes import speed
# Do geo math in US National Atlas Equal Area
P2163 = pyproj.Proj(init='epsg:2163')

ICONFILE = "http://mesonet.agron.iastate.edu/request/grx/storm_attribute.png"
SECONDS = np.array([15*60, 30*60, 45*60, 60*60])
RADARS = """pabc,pacr,60.792,-161.876,57,13,AK,Bethel
pacg,pajk,56.853,-135.528,82,13,AK,Biorka Island
pahg,pafc,60.726,-151.351,108,13,AK,Kenai
pakc,pacr,58.68,-156.627,43,13,AK,King Salmon
paih,pafc,59.462,-146.301,40,13,AK,Middleton Island
paec,pafg,64.512,-165.293,27,13,AK,Nome
papd,pafg,65.035,-147.501,825,13,AK,Pedro Dome
kbmx,kbmx,33.172,-86.77,231,13,AL,Birmingham
keox,ktae,31.46,-85.459,163,13,AL,Fort Rucker
khtx,khun,34.931,-86.084,566,13,AL,Huntsville
kmxx,kbmx,32.537,-85.79,170,13,AL,Maxwell AFB
kmob,kmob,30.679,-88.24,88,13,AL,Mobile
ksrx,ktsa,35.29,-94.362,224,13,AR,Fort Smith
klzk,klzk,34.836,-92.262,197,13,AR,Little Rock
kfsx,kfgz,34.574,-111.198,2290,13,AZ,Flagstaff
kiwa,kpsr,33.289,-111.67,434,29,AZ,Phoenix
kemx,ktwc,31.894,-110.63,1621,13,AZ,Tucson
kyux,kpsr,32.495,-114.656,72,13,AZ,Yuma
kbbx,ksto,39.496,-121.632,67,13,CA,Beale AFB
keyx,kvef,35.098,-117.561,875,13,CA,Edwards AFB
kbhx,keka,40.499,-124.292,766,13,CA,Eureka
kvtx,klox,34.412,-119.179,855,13,CA,Los Angeles
kdax,ksto,38.501,-121.678,43,13,CA,Sacramento
knkx,ksgx,32.919,-117.041,320,13,CA,San Diego
kmux,kmtr,37.155,-121.898,1082,13,CA,San Francisco
khnx,khnx,36.314,-119.632,103,13,CA,San Joaquin Valley
ksox,ksgx,33.818,-117.636,946,13,CA,Santa Ana Mountains
kvbx,klox,34.839,-120.398,412,13,CA,Vandenberg AFB
kftg,kbou,39.786,-104.546,1709,13,CO,Denver/Boulder
kgjx,kgjt,39.062,-108.214,3078,13,CO,Grand Junction
kpux,kpub,38.46,-104.181,1634,13,CO,Pueblo
kdox,kakq,38.826,-75.44,49,13,DE,Dover AFB
kevx,kmob,30.565,-85.922,67,13,FL,Eglin AFB
kjax,kjax,30.485,-81.702,48,13,FL,Jacksonville
kbyx,kkey,24.597,-81.703,27,13,FL,Key West
kmlb,kmlb,28.113,-80.654,35,13,FL,Melbourne
kamx,kmfl,25.611,-80.413,33,13,FL,Miami
ktlh,ktae,30.398,-84.329,53,13,FL,Tallahassee
ktbw,ktbw,27.705,-82.402,37,13,FL,Tampa
kffc,kffc,33.363,-84.566,296,13,GA,Atlanta
kvax,kjax,30.89,-83.002,100,13,GA,Moody AFB
kjgx,kffc,32.675,-83.351,188,13,GA,Robins AFB
pgua,pgum,13.456,144.811,117,13,GU,Andersen AFB
phki,phfo,21.894,-159.552,103,13,HI,Kauai
phkm,phfo,20.125,-155.778,1208,13,HI,Kohala
phmo,phfo,21.133,-157.18,440,13,HI,Molokai
phwa,phfo,19.095,-155.569,445,13,HI,South Shore
kdmx,kdmx,41.731,-93.723,333,13,IA,Des Moines
kdvn,kdvn,41.612,-90.581,259,13,IA,Quad Cities
kcbx,kboi,43.49,-116.236,966,13,ID,Boise
ksfx,kpih,43.106,-112.686,1383,13,ID,Pocatello
klot,klot,41.604,-88.085,231,13,IL,Chicago
kilx,kilx,40.15,-89.337,222,13,IL,Lincoln
kvwx,kpah,38.26,-87.724,191,13,IN,Evansville
kiwx,kiwx,41.359,-85.7,321,13,IN,Fort Wayne
kind,kind,39.708,-86.28,270,13,IN,Indianapolis
kddc,kddc,37.761,-99.969,814,13,KS,Dodge City
kgld,kgld,39.367,-101.7,1132,13,KS,Goodland
ktwx,ktop,38.997,-96.232,431,13,KS,Topeka
kict,kict,37.654,-97.443,427,29,KS,Wichita
khpx,kpah,36.737,-87.285,190,13,KY,Fort Campbell
kjkl,kjkl,37.591,-83.313,445,13,KY,Jackson
klvx,klmk,37.975,-85.944,253,13,KY,Louisville
kpah,kpah,37.068,-88.772,153,13,KY,Paducah
kpoe,klch,31.155,-92.976,143,13,LA,Fort Polk
klch,klch,30.125,-93.216,41,13,LA,Lake Charles
klix,klix,30.337,-89.825,54,13,LA,New Orleans
kshv,kshv,32.451,-93.841,117,13,LA,Shreveport
kbox,kbox,41.956,-71.137,70,13,MA,Boston
kcbw,kcar,46.039,-67.806,261,13,ME,Caribou
kgyx,kgyx,43.891,-70.256,144,13,ME,Portland
kdtx,kdtx,42.7,-83.472,370,13,MI,Detroit
kapx,kapx,44.906,-84.72,475,13,MI,Gaylord
kgrr,kgrr,42.894,-85.545,266,13,MI,Grand Rapids
kmqt,kmqt,46.531,-87.548,464,13,MI,Marquette
kdlh,kdlh,46.837,-92.21,470,13,MN,Duluth
kmpx,kmpx,44.849,-93.565,335,13,MN,Minneapolis
keax,keax,38.81,-94.264,334,13,MO,Kansas City
ksgf,ksgf,37.235,-93.4,419,13,MO,Springfield
klsx,klsx,38.699,-90.683,219,13,MO,St. Louis
kgwx,kjan,33.897,-88.329,179,13,MS,Columbus AFB
kdgx,kjan,32.28,-89.984,185,13,MS,Jackson
kblx,kbyz,45.854,-108.607,1128,13,MT,Billings
kggw,kggw,48.206,-106.625,726,13,MT,Glasgow
ktfx,ktfx,47.46,-111.385,1159,13,MT,Great Falls
kmsx,kmso,47.041,-113.986,2431,13,MT,Missoula
kmhx,kmhx,34.776,-76.876,43,29,NC,Morehead City
krax,krah,35.665,-78.49,140,13,NC,Raleigh/Durham
kltx,kilm,33.989,-78.429,44,13,NC,Wilmington
kbis,kbis,46.771,-100.76,534,13,ND,Bismarck
kmvx,kfgf,47.528,-97.325,329,13,ND,Grand Forks
kmbx,kbis,48.393,-100.864,484,13,ND,Minot AFB
kuex,kgid,40.321,-98.442,626,13,NE,Hastings
klnx,klbf,41.958,-100.576,948,13,NE,North Platte
koax,koax,41.32,-96.367,384,13,NE,Omaha
kabx,kabq,35.15,-106.824,1813,13,NM,Albuquerque
kfdx,kabq,34.634,-103.619,1431,13,NM,Cannon AFB
khdx,kepz,33.077,-106.12,1301,13,NM,Holloman AFB
klrx,klkn,40.74,-116.803,2101,13,NV,Elko
kesx,kvef,35.701,-114.891,1508,13,NV,Las Vegas
krgx,krev,39.754,-119.462,2559,13,NV,Reno
kenx,kaly,42.586,-74.064,589,13,NY,Albany
kbgm,kbgm,42.2,-75.985,519,13,NY,Binghamton
kbuf,kbuf,42.949,-78.737,240,13,NY,Buffalo
ktyx,kbuf,43.756,-75.68,597,13,NY,Montague
kokx,kokx,40.865,-72.864,60,13,NY,Upton
kcle,kcle,41.413,-81.86,262,13,OH,Cleveland
kiln,kiln,39.42,-83.822,356,13,OH,Wilmington
kfdr,koun,34.362,-98.977,399,13,OK,Frederick
ktlx,koun,35.333,-97.278,389,13,OK,Oklahoma City
kinx,ktsa,36.175,-95.564,228,13,OK,Tulsa
kvnx,koun,36.741,-98.128,383,29,OK,Vance AFB
kmax,kmfr,42.081,-122.717,2302,13,OR,Medford
kpdt,kpdt,45.691,-118.853,481,13,OR,Pendleton
krtx,kpqr,45.715,-122.965,526,13,OR,Portland
kdix,kphi,39.947,-74.411,70,13,PA,Philadelphia
kpbz,kpbz,40.532,-80.218,385,29,PA,Pittsburgh
kccx,kctp,40.923,-78.004,757,13,PA,State College
tjua,tjsj,18.116,-66.078,901,13,PR,Puerto Rico
kclx,kchs,32.655,-81.042,69,13,SC,Charleston
kcae,kcae,33.949,-81.119,104,13,SC,Columbia
kgsp,kgsp,34.883,-82.22,325,13,SC,Greer
kabr,kabr,45.456,-98.413,421,13,SD,Aberdeen
kudx,kunr,44.125,-102.83,973,13,SD,Rapid City
kfsd,kfsd,43.588,-96.729,455,13,SD,Sioux Falls
kmrx,kmrx,36.168,-83.402,437,13,TN,Knoxville
knqa,kmeg,35.345,-89.873,132,13,TN,Memphis
kohx,kohx,36.247,-86.563,206,13,TN,Nashville
kama,kama,35.233,-101.709,1128,13,TX,Amarillo
kbro,kbro,25.916,-97.419,26,13,TX,Brownsville
kgrk,kfwd,30.722,-97.383,183,13,TX,Central Texas
kcrp,kcrp,27.784,-97.511,43,13,TX,Corpus Christi
kfws,kfwd,32.573,-97.303,236,13,TX,Dallas/Fort Worth
kdyx,ksjt,32.538,-99.254,481,13,TX,Dyess AFB
kepz,kepz,31.873,-106.698,1285,13,TX,El Paso
khgx,khgx,29.472,-95.079,35,13,TX,Houston
kdfx,kewx,29.273,-100.28,364,13,TX,Laughlin AFB
klbb,klub,33.654,-101.814,1029,13,TX,Lubbock
kmaf,kmaf,31.943,-102.189,902,13,TX,Midland/Odessa
ksjt,ksjt,31.371,-100.492,610,13,TX,San Angelo
kewx,kewx,29.704,-98.029,233,13,TX,San Antonio
kicx,kslc,37.591,-112.862,3278,13,UT,Cedar City
kmtx,kslc,41.263,-112.448,2009,13,UT,Salt Lake City
kfcx,krnk,37.024,-80.274,903,13,VA,Blacksburg
klwx,klwx,38.976,-77.487,123,13,VA,Sterling
kakq,kakq,36.984,-77.008,77,13,VA,Wakefield
kcxx,kbtv,44.511,-73.166,131,13,VT,Burlington
klgx,ksew,47.116,-124.107,111,13,WA,Langley Hill
katx,ksew,48.195,-122.496,195,13,WA,Seattle/Tacoma
kotx,kotx,47.681,-117.626,746,13,WA,Spokane
kgrb,kgrb,44.499,-88.111,245,13,WI,Green Bay
karx,karx,43.823,-91.191,413,13,WI,La Crosse
kmkx,kmkx,42.968,-88.551,311,13,WI,Milwaukee
krlx,krlx,38.311,-81.723,369,13,WV,Charleston
kcys,kcys,41.152,-104.806,1887,13,WY,Cheyenne
kriw,kriw,43.066,-108.477,1716,13,WY,Riverton"""


def rotate(x, y, rad):
    return [(x * math.cos(-rad) - y * math.sin(-rad)),
            (x * math.sin(-rad) + y * math.cos(-rad))]


def dir2ccwrot(mydir):
    # Convert to CCW
    if mydir >= 270 and mydir <= 360:
        return 0 - (mydir - 270)
    if mydir >= 180 and mydir < 270:
        return 270 - mydir
    if mydir >= 90 and mydir < 180:
        return 180 - (mydir - 90)
    if mydir >= 0 and mydir < 90:
        return 180 + (90 - mydir)


def rabbit_tracks(row):
    """Generate a rabbit track for this attr"""
    res = ""
    if row['sknt'] is None or row['sknt'] <= 5 or row['drct'] is None:
        return res
    # 5 carrots at six minutes to get 30 minutes?
    lat0 = row['lat']
    lon0 = row['lon']
    drct = row['drct']
    sknt = row['sknt']
    x0, y0 = P2163(lon0, lat0)
    smps = speed(sknt, 'KTS').value('MPS')
    angle = dir2ccwrot(drct)
    rotation = (drct + 180) % 360
    rad = math.radians(angle)
    x = x0 + math.cos(rad) * smps * SECONDS
    y = y0 + math.sin(rad) * smps * SECONDS
    # Draw white line out 30 minutes
    lons, lats = P2163(x, y, inverse=True)
    res += ("Line: 1, 0, \"Cell [%s]\"\n"
            "%.4f, %.4f\n"
            "%.4f, %.4f\n"
            "END:\n") % (row['storm_id'],
                         lat0, lon0, lats[-1], lons[-1])
    for i in range(3):
        res += ("Icon: %.4f,%.4f,%.0f,1,10,\"+%.0f min\"\n"
                ) % (lats[i], lons[i], rotation, (i+1)*15)
    return res


def produce_content(nexrad):
    """Do Stuff"""
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    limiter = ''
    threshold = 999
    title = "IEM NEXRAD L3 Attributes"
    if nexrad != '':
        limiter = " and nexrad = '%s' " % (nexrad,)
        title = "IEM %s NEXRAD L3 Attributes" % (nexrad,)
        threshold = 45
    cursor.execute("""
        SELECT *, ST_x(geom) as lon, ST_y(geom) as lat,
        valid at time zone 'UTC' as utc_valid
        from nexrad_attributes WHERE valid > now() - '15 minutes'::interval
    """ + limiter)
    res = ("Refresh: 3\n"
           "Threshold: %s\n"
           "Title: %s\n"
           "IconFile: 1, 32, 32, 16, 16, \"%s\"\n"
           "Font: 1, 11, 1, \"Courier New\"\n"
           ) % (threshold, title, ICONFILE)
    for row in cursor:
        text = ("K%s [%s] %s Z\\n"
                "Drct: %s Speed: %s kts\\n"
                ) % (row['nexrad'], row['storm_id'],
                     row['utc_valid'].strftime("%H:%I"), row['drct'],
                     row['sknt'])
        icon = 9
        if (row["tvs"] != "NONE" or row["meso"] != "NONE"):
            text += "TVS: %s MESO: %s\\n" % (row['tvs'], row['meso'])
        if (row['poh'] > 0 or row['posh'] > 0):
            text += "POH: %s POSH: %s MaxSize: %s\\n" % (row['poh'],
                                                         row['posh'],
                                                         row['max_size'])
            icon = 2
        if row['meso'] != 'NONE':
            meso = int(row['meso'])
            if meso < 4:
                icon = 8
            elif meso < 7:
                icon = 7
            else:
                icon = 6
        if row['tvs'] != 'NONE':
            icon = 5
        res += ("Object: %.4f,%.4f\n"
                "Threshold: 999\n"
                "Icon: 0,0,0,1,%s,\"%s\"\n"
                "END:\n"
                ) % (row['lat'], row['lon'], icon, text)
        res += rabbit_tracks(row)
    return res


def main():
    """ Go Main Go """
    form = cgi.FieldStorage()
    nexrad = form.getfirst('nexrad', '').upper()[:3]
    if nexrad == '':
        lon = form.getfirst('lon')
        if lon is not None:
            for line in RADARS.split("\n"):
                if line.find(lon) > 0:
                    nexrad = line[1:4].upper()

    mckey = "/request/grx/i3attr|%s" % (nexrad,)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = produce_content(nexrad)
        mc.set(mckey, res, 60)
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write(res)

if __name__ == '__main__':
    main()
