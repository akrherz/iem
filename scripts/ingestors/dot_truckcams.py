"""
  Iowa DOT Truck dash camera imagery.  Save this to the IEM archives

  /YYYY/mm/dd/camera/idot_trucks/keyhash/keyhash_timestamp.jpg
"""
import urllib2
import json
import psycopg2
import pytz
import datetime
import subprocess
import tempfile
import os

URI = ("https://geonexusr.iowadot.gov/arcgis/rest/services/Operations/"
       "Truck_Images/MapServer/3/query?outFields=*&outSR=4326&"
       "f=json&where=PHOTO_UID%3E0&returnGeometry=true&returnIdsOnly=false")


def get_label(attrs):
    '''Figure out the site label given the attributes, this will change later
    '''
    return attrs['PHOTO_URL'].split("/")[-1].split("_")[0]


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
    try:
        data = json.loads(urllib2.urlopen(URI, timeout=30).read())
    except:
        return
    if len(data.get('features', [])) == 0:
        return
    POSTGIS = psycopg2.connect(database='postgis', host='iemdb')
    cursor = POSTGIS.cursor()

    cursor.execute("""SELECT label, idnum from idot_dashcam_current""")
    current = {}
    for row in cursor:
        current[row[0]] = row[1]

    for feat in data['features']:
        logdt = feat['attributes']['PHOTO_FILEDATE']
        ts = datetime.datetime.utcfromtimestamp(logdt/1000.)
        valid = valid.replace(year=ts.year, month=ts.month, day=ts.day,
                              hour=ts.hour, minute=ts.minute,
                              second=ts.second)
        label = get_label(feat['attributes'])
        idnum = feat['attributes']['PHOTO_UID']
        if idnum <= current.get(label, 0):
            continue

        utc = valid.astimezone(pytz.timezone("UTC"))
        # Go get the URL for saving!
        # print label, utc, feat['attributes']['PHOTO_URL']
        try:
            image = urllib2.urlopen(feat['attributes']['PHOTO_URL'],
                                    timeout=15).read()
        except urllib2.URLError, exp:
            print(('dot_truckcams.py dl fail |%s| %s'
                   ) % (exp, feat['attributes']['PHOTO_URL']))
            continue
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(image)
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

        geom = 'SRID=4326;POINT(%s %s)' % (feat['geometry']['x'],
                                           feat['geometry']['y'])
        cursor.execute("""
            INSERT into idot_dashcam_current(label, valid, idnum,
            geom) VALUES (%s, %s, %s, %s)
        """, (label, valid, idnum, geom))

    cursor.close()
    POSTGIS.commit()
    POSTGIS.close()

if __name__ == '__main__':
    workflow()
