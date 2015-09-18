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
    elif text == "FAIL":
        return "%s[FAIL]%s" % (bcolors.FAIL, bcolors.ENDC)
    return text


def set_county(iemid, ugc, ugcname):
    mcursor2.execute("""
        UPDATE stations SET county = %s, ugc_county = %s
        WHERE iemid = %s
    """, (ugcname, ugc, iemid))


def set_zone(iemid, ugc):
    mcursor2.execute("""
        UPDATE stations SET ugc_zone = %s
        WHERE iemid = %s
    """, (ugc, iemid))


def logic(ugccode, iemid, station, name, network, lon, lat, state):
    """Our logic"""
    pcursor.execute("""
        SELECT ugc, name from ugcs WHERE
        ST_Contains(geom, ST_GeomFromText('Point(%s %s)',4326))
        and substr(ugc,1,3) = '%s' and end_ts is null
    """ % (lon, lat, state + ugccode))

    result = False
    if pcursor.rowcount != 1:
        # Okay, so perhaps this site is offshore slightly, lets look for the
        # nearest county
        pcursor.execute("""
            SELECT ugc, name,
            ST_Distance(geom, ST_GeomFromText('Point(%s %s)',4326)) as d
            from ugcs WHERE substr(ugc,1,3) = '%s' and end_ts is null and
            ST_Distance(geom, ST_GeomFromText('Point(%s %s)',4326)) < 0.5
            ORDER by d ASC LIMIT 1
        """ % (lon, lat, state + ugccode, lon, lat))
        if pcursor.rowcount == 1:
            (ugc, ugcname, dist) = pcursor.fetchone()
            print(("%s set_county[%s] ID: %s Net: %s: St: %s "
                   "UGC: %s Dist: %.2f"
                   ) % (msg('OK'), ugccode, station, network, state, ugc,
                        dist))
            if ugccode == 'C':
                set_county(iemid, ugc, ugcname)
            else:
                set_zone(iemid, ugc)
            result = True
        else:
            print(("%s set_county[%s] ID:%s Net:%s St:%s "
                   "Lon:%.4f Lat:%.4f\nhttp://mesonet.agron.iastate.edu/sites/"
                   "site.php?station=%s&network=%s"
                   "") % (msg("FAIL"), ugccode, station, network, state,
                          lon, lat, station, network))
            result = False

    else:
        (ugc, ugcname) = pcursor.fetchone()
        print(("%s %s IEMID: %s SID: %s Network: %s to: %s [%s]"
               ) % (msg("OK"), ugccode, iemid, station, network,
                    ugcname, ugc))
        if ugccode == 'C':
            set_county(iemid, ugc, ugcname)
        else:
            set_zone(iemid, ugc)
        result = True
    return result

# Get listing of stations without a county set
mcursor.execute("""SELECT iemid, id, name, network, ST_x(geom), ST_y(geom),
    state from stations WHERE (county is null or ugc_county is null
    or ugc_zone is null) and country = 'US' and state is not null
    and state not in ('PR', 'DC', 'GU', 'PU', 'P1', 'P2', 'P3', 'P4', 'P5')
    ORDER by modified DESC
    """)

FAILURES = 0
for row in mcursor:
    iemid = row[0]
    station = row[1]
    name = row[2]
    network = row[3]
    lon = row[4]
    lat = row[5]
    state = row[6]
    if not logic("C", iemid, station, name, network, lon, lat, state):
        FAILURES += 1
    if not logic("Z", iemid, station, name, network, lon, lat, state):
        FAILURES += 1

    if FAILURES > 10:
        break

mcursor.close()
mcursor2.close()
pcursor.close()
MESOSITE.commit()
