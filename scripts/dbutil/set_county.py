"""
  Need to set station metadata for county name for a given site...
"""

import psycopg2
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
POSTGIS = psycopg2.connect(database='postgis', host='iemdb')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()
pcursor = POSTGIS.cursor()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def msg(text):
    if text == 'OK':
        return "%s[ OK ]%s" % (bcolors.OKGREEN, bcolors.ENDC)


# Get listing of stations without a county set
mcursor.execute("""SELECT iemid, id, name, network, ST_x(geom), ST_y(geom),
    state from stations WHERE (county is null or ugc_county is null
    or ugc_zone is null) and country = 'US' and state is not null
    and state not in ('PR', 'DC', 'GU', 'PU', 'P1', 'P3', 'P4', 'P5')
    ORDER by modified DESC LIMIT 50
    """)

for row in mcursor:
    iemid = row[0]
    station = row[1]
    name = row[2]
    network = row[3]
    lon = row[4]
    lat = row[5]
    state = row[6]

    # Lets attempt to find the county!
    pcursor.execute("""SELECT ugc, name from ugcs WHERE
    ST_Contains(geom, ST_GeomFromText('Point(%s %s)',4326))
    and substr(ugc,1,3) = '%s' and end_ts is null""" % (lon, lat, state + "C"))

    if pcursor.rowcount != 1:
        print(("%s[FAIL]%s set_county[cnty] ID:%s Net:%s St:%s "
               "Lon: %.4f Lat: %.4f\nhttp://mesonet.agron.iastate.edu/sites/"
               "site.php?station=%s&network=%s"
               "") % (bcolors.FAIL, bcolors.ENDC, station, network, state,
                      lon, lat, station, network))
        # Okay, so perhaps this site is offshore slightly, lets look for the
        # nearest county
        pcursor.execute("""
        SELECT ugc, name,
        ST_Distance(geom, ST_GeomFromText('Point(%s %s)',4326)) as d
        from ugcs WHERE substr(ugc,1,3) = '%s' and end_ts is null and
        ST_Distance(geom, ST_GeomFromText('Point(%s %s)',4326)) < 0.5
        ORDER by d ASC LIMIT 1
        """ % (lon, lat, state + 'C', lon, lat))
        if pcursor.rowcount == 1:
            (ugc, ugcname, dist) = pcursor.fetchone()
            print(("%s [cnty_nearest] ID: %s Net: %s: St: %s "
                   "UGC: %s Dist: %.2f"
                   ) % (msg('OK'), station, network, state, ugc, dist))
            mcursor2.execute("""
            UPDATE stations SET county = %s, ugc_county = %s
            WHERE iemid = %s""", (ugcname, ugc, iemid))
    else:
        (ugc, ugcname) = pcursor.fetchone()
        print(("%s[ OK ]%s IEMID: %s SID: %s Network: %s to county: %s [%s]"
               "") % (bcolors.OKGREEN, bcolors.ENDC, iemid, station, network,
                      ugcname, ugc))
        mcursor2.execute("""
            UPDATE stations SET county = %s, ugc_county = %s
            WHERE iemid = %s""", (ugcname, ugc, iemid))

    # Lets attempt to find the zone!
    pcursor.execute("""SELECT ugc, name from ugcs WHERE
    ST_Contains(geom, ST_GeomFromText('Point(%s %s)',4326))
    and substr(ugc,1,3) = '%s' and end_ts is null
    ORDER by begin_ts DESC LIMIT 1""" % (lon, lat, state + "Z"))

    if pcursor.rowcount != 1:
        print(("%s[FAIL]%s set_county[zone] ID:%s Network:%s State:%s "
               "Lon: %.2f Lat: %.2f\n"
               "http://mesonet.agron.iastate.edu/sites/site.php"
               "?station=%s&network=%s"
               "") % (bcolors.FAIL, bcolors.ENDC, station, network, state,
                      lon, lat, station, network))
    else:
        (ugc, ugcname) = pcursor.fetchone()
        print(("%s[ OK ]%s set_county IEMID: %s SID: %s Network: %s to "
               "fx zone: %s [%s]"
               "") % (bcolors.OKGREEN, bcolors.ENDC, iemid, station, network,
                      ugcname, ugc))
        mcursor2.execute("""
            UPDATE stations SET ugc_zone = %s
            WHERE iemid = %s""", (ugc, iemid))

mcursor.close()
mcursor2.close()
pcursor.close()
MESOSITE.commit()
