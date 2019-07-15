"""Update postgis CWA table

It is unclear that this script is even needed anymore.
"""
from __future__ import print_function
import sys
import os
import zipfile

import requests
import geopandas as gpd
from pyiem.util import get_dbconn
POSTGIS = get_dbconn('postgis')


def main():
    """Go Main!"""
    cursor = POSTGIS.cursor()

    # Get the name of the file we wish to download
    if len(sys.argv) != 2:
        print('ERROR: You need to specify the file date to download ')
        print('Example:  python cwa_update.py w_01ap14a')
        sys.exit(0)

    DATESTAMP = sys.argv[1]

    # Change Directory to /tmp, so that we can rw
    os.chdir('/tmp')

    zipfn = "%s.zip" % (DATESTAMP,)
    if not os.path.isfile(zipfn):
        req = requests.get(('http://www.weather.gov/source/gis/Shapefiles/'
                            'WSOM/%s') % (zipfn,))
        if req.status_code != 200:
            print('dlfailed')
            return
        print('Downloading %s ...' % (zipfn,))
        o = open(zipfn, 'wb')
        o.write(req.content)
        o.close()

    print('Unzipping')
    zipfp = zipfile.ZipFile(zipfn, 'r')
    shpfn = None
    for name in zipfp.namelist():
        print('    Extracting %s' % (name,))
        o = open(name, 'wb')
        o.write(zipfp.read(name))
        o.close()
        if name[-3:] == 'shp':
            shpfn = name

    print('Processing')
    # Now we are ready to dance!
    df = gpd.read_file(shpfn)
    df['area'] = df['geometry'].area
    countnoop = 0
    countnew = 0
    wfos = {}
    for _, row in df.iterrows():
        wfo = row['WFO']
        cwa = row['CWA']
        area = row['area']

        if wfo in wfos:
            if area < wfos[wfo]:
                print(('Skipping %s [area: %s], since we had a '
                       'previously bigger one') % (wfo, area))
                continue
        wfos[wfo] = area

        # OK, lets see if this UGC is new
        cursor.execute("""
            SELECT cwa from cwa where cwa = %s and
            the_geom = ST_Multi(ST_SetSRID(ST_GeomFromEWKT(%s),4326))
            """, (cwa, row['geometry'].wkt))

        # NOOP
        if cursor.rowcount == 1:
            countnoop += 1
            continue

        # Finally, insert the new geometry
        cursor.execute("""
        UPDATE cwa
        SET the_geom = ST_Multi(ST_SetSRID(ST_GeomFromEWKT(%s),4326))
        WHERE cwa = %s
        """, (row['geometry'].wkt, cwa))
        countnew += 1

    print('NOOP: %s UPDATED: %s' % (countnoop, countnew))

    cursor.close()
    POSTGIS.commit()
    POSTGIS.close()
    print('Done!')


if __name__ == '__main__':
    main()
