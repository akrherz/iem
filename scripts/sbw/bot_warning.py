import math
import psycopg2.extras
import pyproj
P2163 = pyproj.Proj(init='epsg:2163')
postgis = psycopg2.connect(database='postgis', host='localhost',
                           port=5555, user='mesonet')
pcursor = postgis.cursor(cursor_factory=psycopg2.extras.DictCursor)
pcursor2 = postgis.cursor()


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


warnX = []
warnY = []
lsrX = []
lsrY = []
rlsrX = []
rlsrY = []
polyX = []
polyY = []
majorX = []
minorX = []
minorY = []
majorY = []
deltaX = []
deltaY = []
dT = []
dXT = []
dDist = []
offsetX = []
offsetY = []
# output = open('xy.dat', 'w')

pcursor.execute("""
    SELECT issue, init_expire, tml_direction, tml_sknt,
    ST_x(tml_geom) as tml_lon, ST_y(tml_geom) as tml_lat, wfo,
    phenomena, significance, eventid from sbw WHERE
    phenomena = 'TO' and status = 'NEW' and wfo = 'IND'
    and issue between '2008-01-01' and '2016-01-01'
    """)
for i, row in enumerate(pcursor):
    issue = row['issue']
    expire = row['init_expire']
    i += 1
    if i % 1000 == 0:
        print('Done %s' % (i,))
    tml_direction = row['tml_direction']
    tml_sknt = row['tml_sknt']
    if float(tml_sknt) == 0:
        continue
    lat = row['tml_lat']
    lon = row['tml_lon']
    if lat is None:
        continue
    xTML, yTML = P2163(lon, lat)
    smps = float(tml_sknt) * 0.514
    # This is the from angle, need to rotate 180 to get the to angle
    angle = dir2ccwrot(tml_direction)
    rad = math.radians(angle)
    print tml_direction, angle, rad

    xTML2 = xTML + math.cos(rad)*smps*1800.  # 30 min
    yTML2 = yTML + math.sin(rad)*smps*1800.  # 30 min
    ulX = xTML + math.cos(rad+math.pi/2.)*10000.
    ulY = yTML + math.sin(rad+math.pi/2.)*10000.  # 10km "north"
    llX = xTML - math.cos(rad+math.pi/2.)*10000.
    llY = yTML - math.sin(rad+math.pi/2.)*10000.  # 10km "south"
    urX = xTML2 + math.cos(rad+math.pi/2.)*10000.
    urY = yTML2 + math.sin(rad+math.pi/2.)*10000.  # 10km "north"
    lrX = xTML2 - math.cos(rad+math.pi/2.)*30000.
    lrY = yTML2 - math.sin(rad+math.pi/2.)*30000.  # 30km "south"

    # Find LSRs
    sql = """
    INSERT into bot_warnings(issue, expire, gtype, wfo,
    geom, eventid, phenomena, significance, status) VALUES ('%s', '%s',
    'P', '%s',
    ST_Transform(ST_GeomFromText('SRID=2163;MULTIPOLYGON(((%s %s, %s %s,
    %s %s, %s %s, %s %s)))'),4326),
    %s, '%s', '%s', 'NEW')
    """ % (issue, expire,
           row['wfo'], llX, llY, ulX, ulY, urX, urY, lrX, lrY, llX, llY,
           row['eventid'], row['phenomena'], row['significance'])
    # print sql
    pcursor2.execute(sql)

pcursor2.close()
postgis.commit()
