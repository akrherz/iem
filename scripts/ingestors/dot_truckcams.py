"""
  Iowa DOT Truck dash camera imagery.  Save this to the IEM archives

  /YYYY/mm/dd/camera/idot_trucks/keyhash/keyhash_timestamp.jpg
"""
import psycopg2
import pytz
import datetime
import subprocess
import tempfile
import os
import requests
import pyproj

P3857 = pyproj.Proj(init='EPSG:3857')
URI = ("http://iowadot.maps.arcgis.com/sharing/rest/content/items/"
       "71846cc4c673428ca35057d6849ee0c6/data")


def get_current_fn(label):
    ''' Return how this is stored for current data '''
    return 'camera/idot_trucks/%s.jpg' % (label,)


def get_archive_fn(label, utc):
    ''' Return how this is stored for current data '''
    return 'camera/idot_trucks/%s/%s_%s.jpg' % (label, label,
                                                utc.strftime("%Y%m%d%H%M"))


def workflow():
    ''' Do stuff '''
    valid = datetime.datetime.now()
    valid = valid.replace(tzinfo=pytz.timezone("America/Chicago"),
                          microsecond=0)
    req = requests.get(URI, timeout=30)
    if req.status_code != 200:
        return
    data = req.json()
    featureset = data['layers'][0].get('featureSet', dict())
    features = featureset.get('features', [])
    POSTGIS = psycopg2.connect(database='postgis', host='iemdb')
    cursor = POSTGIS.cursor()

    cursor.execute("""SELECT label, idnum from idot_dashcam_current""")
    current = {}
    for row in cursor:
        current[row[0]] = row[1]

    for feat in features:
        logdt = feat['attributes']['PHOTO_FILEDATE']
        if logdt is None:
            continue
        ts = datetime.datetime.utcfromtimestamp(logdt/1000.)
        valid = valid.replace(year=ts.year, month=ts.month, day=ts.day,
                              hour=ts.hour, minute=ts.minute,
                              second=ts.second)
        label = feat['attributes']['PHOTO_ANUMBER']
        idnum = feat['attributes']['PHOTO_UID']
        if idnum <= current.get(label, 0):
            continue

        utc = valid.astimezone(pytz.timezone("UTC"))
        # Go get the URL for saving!
        # print label, utc, feat['attributes']['PHOTO_URL']
        req = requests.get(feat['attributes']['PHOTO_URL'], timeout=15)
        if req.status_code != 200:
            print(('dot_truckcams.py dl fail |%s| %s'
                   ) % (req.status_code, feat['attributes']['PHOTO_URL']))
            continue
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(req.content)
        tmp.close()
        cmd = ("/home/ldm/bin/pqinsert -p 'plot ac %s %s %s jpg' %s"
               ) % (utc.strftime("%Y%m%d%H%M"), get_current_fn(label),
                    get_archive_fn(label, utc), tmp.name)
        proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        _ = proc.stderr.read()
        # if output != "":
        #    print '-------------------------'
        #    print '  dot_truckcams.py pqinsert stderr result:'
        #    print output
        #    print 'label: %s timestamp: %s' % (label, utc)
        #    print 'URI: %s' % (feat['attributes']['PHOTO_URL'],)
        #    print '-------------------------\n'
        os.unlink(tmp.name)

        pt = P3857(feat['geometry']['x'], feat['geometry']['y'], inverse=True)
        geom = 'SRID=4326;POINT(%s %s)' % (pt[0], pt[1])
        cursor.execute("""
            INSERT into idot_dashcam_current(label, valid, idnum,
            geom) VALUES (%s, %s, %s, %s)
        """, (label, valid, idnum, geom))

    cursor.close()
    POSTGIS.commit()
    POSTGIS.close()

if __name__ == '__main__':
    workflow()
