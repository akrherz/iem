"""
  Need to set station metadata for county name for a given site...
"""

import psycopg2
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
POSTGIS = psycopg2.connect(database='postgis', host='iemdb')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()
pcursor = POSTGIS.cursor()

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
        print(("set_county[cnty] fail ID:%s Net:%s St:%s "
               "Lon: %.4f Lat: %.4f\nhttp://mesonet.agron.iastate.edu/sites/"
               "site.php?station=%s&network=%s"
               "") % (station, network, state, lon, lat, station, network))
    else:
        (ugc, ugcname) = pcursor.fetchone()
        print(("Assinging IEMID: %s SID: %s Network: %s to county: %s [%s]"
               "") % (iemid, station, network, ugcname, ugc))
        mcursor2.execute("""
            UPDATE stations SET county = %s, ugc_county = %s
            WHERE iemid = %s""", (ugcname, ugc, iemid))

    # Lets attempt to find the zone!
    pcursor.execute("""SELECT ugc, name from ugcs WHERE
    ST_Contains(geom, ST_GeomFromText('Point(%s %s)',4326))
    and substr(ugc,1,3) = '%s' and end_ts is null""" % (lon, lat, state + "Z"))

    if pcursor.rowcount != 1:
        print(("set_county[zone] fail ID:%s Network:%s State:%s "
               "Lon: %.2f Lat: %.2f"
               "") % (station, network, state, lon, lat))
    else:
        (ugc, ugcname) = pcursor.fetchone()
        print(("set_county IEMID: %s SID: %s Network: %s to fx zone: %s [%s]\n"
               "http://mesonet.agron.iastate.edu/sites/site.php"
               "?station=%s&network=%s"
               "") % (iemid, station, network, ugcname, ugc, station, network))
        mcursor2.execute("""
            UPDATE stations SET county = %s, ugc_county = %s
            WHERE iemid = %s""", (ugcname, ugc, iemid))

mcursor.close()
mcursor2.close()
pcursor.close()
MESOSITE.commit()
