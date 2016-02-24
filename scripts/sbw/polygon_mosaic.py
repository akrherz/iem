"""
  Generate an overview image of storm based warnings for website display
"""
import psycopg2.extras
import mapscript
import datetime
import pytz
import sys
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)
pcursor2 = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Preparation
sortOpt = sys.argv[1]
ts = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
sts = ts.replace(tzinfo=pytz.timezone("UTC"), hour=0, minute=0, second=0,
                 microsecond=0)
if len(sys.argv) == 5:
    sts = sts.replace(year=int(sys.argv[1]), month=int(sys.argv[2]),
                      day=int(sys.argv[3]))
    sortOpt = sys.argv[4]

ets = sts + datetime.timedelta(hours=24)

opts = {'W': {'fnadd': '-wfo',
              'sortby': 'wfo ASC, phenomena ASC, eventid ASC'},
        'S': {'fnadd': '', 'sortby': 'size DESC'},
        'T': {'fnadd': '-time', 'sortby': 'issue ASC'}}

# Defaults
thumbpx = 100
cols = 10

# Find largest polygon either in height or width
sql = """SELECT *, ST_area2d(ST_transform(geom,2163)) as size,
  (ST_xmax(ST_transform(geom,2163)) -
   ST_xmin(ST_transform(geom,2163))) as width,
  (ST_ymax(ST_transform(geom,2163)) -
   ST_ymin(ST_transform(geom,2163))) as height
  from sbw_%s WHERE status = 'NEW' and issue >= '%s' and issue < '%s' and
  phenomena IN ('TO','SV') """ % (sts.year, sts, ets)
pcursor.execute(sql)

maxDimension = 0
mybuffer = 10000
i = 0
torCount = 0
torSize = 0
svrCount = 0
svrSize = 0
for row in pcursor:
    w = float(row['width'])
    h = float(row['height'])
    if w > maxDimension:
        maxDimension = w
    if h > maxDimension:
        maxDimension = h

    if row['phenomena'] == "SV":
        svrCount += 1
        svrSize += float(row['size'])
    if row['phenomena'] == "TO":
        torCount += 1
        torSize += float(row['size'])
    i += 1

sql = """
    SELECT phenomena, sum( ST_area2d(ST_transform(u.geom,2163)) ) as size
    from warnings_%s w JOIN ugcs u on (u.gid = w.gid)
    WHERE issue >= '%s' and issue < '%s' and
    significance = 'W' and phenomena IN ('TO','SV') GROUP by phenomena
""" % (sts.year, sts, ets)

pcursor.execute(sql)
for row in pcursor:
    if row['phenomena'] == "TO":
        totalTorCar = 100.0 * (1.0 - (torSize / float(row['size'])))
    if row['phenomena'] == "SV":
        totalSvrCar = 100.0 * (1.0 - (svrSize / float(row['size'])))

# Make mosaic image
header = 35
mosaic = Image.new('RGB', (thumbpx*cols, ((int(i/cols)+1)*thumbpx) + header))
font = ImageFont.truetype('/mesonet/data/gis/static/fonts/veramono.ttf', 12)
font10 = ImageFont.truetype('/mesonet/data/gis/static/fonts/veramono.ttf', 10)
font2 = ImageFont.truetype('/mesonet/data/gis/static/fonts/veramono.ttf', 18)
draw = ImageDraw.Draw(mosaic)

imagemap = open('imap.txt', 'w')
utcnow = datetime.datetime.utcnow()
imagemap.write("<!-- %s %s -->\n" % (utcnow.strftime("%Y-%m-%d %H:%M:%S"),
                                     sortOpt))
imagemap.write("<map name='mymap'>\n")

# Find my polygons
sql = """
    SELECT *, ST_area2d(ST_transform(geom,2163)) as size,
    (ST_xmax(ST_transform(geom,2163)) +
     ST_xmin(ST_transform(geom,2163))) /2.0 as xc,
    (ST_ymax(ST_transform(geom,2163)) +
     ST_ymin(ST_transform(geom,2163))) /2.0 as yc
    from sbw_%s WHERE status = 'NEW' and issue >= '%s' and issue < '%s' and
    phenomena IN ('TO','SV') and eventid is not null ORDER by %s
""" % (sts.year, sts, ets, opts[sortOpt]['sortby'])
pcursor.execute(sql)

# Write metadata to image
tmp = Image.open("logo_small.png")
mosaic.paste(tmp, (3, 2))
s = "IEM Summary of NWS Storm Based Warnings issued %s UTC" % (
                                            sts.strftime("%d %b %Y"), )
(w, h) = font2.getsize(s)
draw.text((54, 3), s, font=font2)

s = "Generated: %s UTC" % (
                datetime.datetime.utcnow().strftime("%d %b %Y %H:%M:%S"), )
draw.text((54, 3 + h), s, font=font10)


if svrCount > 0:
    s = ("%3i SVR: Avg Size %5.0f km^2 CAR: %.0f%%"
         ) % (svrCount, (svrSize / float(svrCount)) / 1000000, totalSvrCar)
    draw.text((54 + w + 10, 8), s, font=font10, fill="#ffff00")

if torCount > 0:
    s = ("%3i TOR: Avg Size %5.0f km^2 CAR: %.0f%%"
         ) % (torCount, (torSize / float(torCount)) / 1000000, totalTorCar)
    draw.text((54 + w + 10, 22), s, font=font10, fill="#ff0000")

if pcursor.rowcount == 0:
    s = "No warnings in database for this date"
    draw.text((100, 78), s, font=font2, fill="#ffffff")

i = 0
for row in pcursor:
    # - Map each polygon]
    x0 = float(row['xc']) - (maxDimension/2.0) - mybuffer
    x1 = float(row['xc']) + (maxDimension/2.0) + mybuffer
    y0 = float(row['yc']) - (maxDimension/2.0) - 2 * mybuffer
    y1 = float(row['yc']) + (maxDimension/2.0)
    mapobj = mapscript.mapObj("polygon.map")
    mapobj.setSize(thumbpx, thumbpx)
    mapobj.setExtent(x0, y0, x1, y1)
    sbw = mapobj.getLayerByName("sbw")
    sbw.data = ("geom from (select phenomena, significance, geom, "
                "random() as oid from sbw_%s WHERE status = 'NEW' "
                " and phenomena = '%s' and significance = '%s' "
                " and eventid = %s and wfo = '%s') as foo "
                " using unique oid using SRID=4326"
                ) % (sts.year,
                     row['phenomena'], row['significance'], row['eventid'],
                     row['wfo'])
    img = mapobj.prepareImage()
    sbw.draw(mapobj, img)
    my = int(i / cols) * thumbpx + header
    mx0 = (i % cols) * thumbpx
    img.save("tmp.png")
    del img, mapobj
    # - Add each polygon to mosaic
    tmp = Image.open("tmp.png")
    mosaic.paste(tmp, (mx0, my))
    del tmp
    os.remove("tmp.png")

    # Compute CAR!
    sql = """
        select sum(ST_area2d(ST_transform(u.geom,2163))) as csize
        from warnings_%s w
        JOIN ugcs u on (u.gid = w.gid) WHERE
        phenomena = '%s' and significance = '%s' and eventid = %s
        and w.wfo = '%s'
        """ % (row['issue'].year, row['phenomena'],
               row['significance'], row['eventid'], row['wfo'])

    pcursor2.execute(sql)
    row2 = pcursor2.fetchone()
    car = "NA"
    carColor = (255, 255, 255)
    if row2 and row2['csize'] is not None:
        csize = float(row2['csize'])
        carF = 100.0 * (1.0 - (row['size'] / csize))
        car = "%.0f" % (carF, )
        if (carF > 75):
            carColor = (0, 255, 0)
        if (carF < 25):
            carColor = (255, 0, 0)

    # Draw Text!
    issue = row['issue']
    s = "%s.%s.%s.%s" % (row['wfo'], row['phenomena'],
                         row['eventid'], issue.strftime("%H%M"))
    # (w, h) = font10.getsize(s)
    # print s, h
    draw.text((mx0 + 2, my + thumbpx - 10), s, font=font10)
    s = "%.0f sq km %s%%" % (row['size']/1000000.0, car)
    draw.text((mx0 + 2, my + thumbpx-(20)), s, font=font10, fill=carColor)

    # Image map
    url = ("/vtec/#%s-O-NEW-K%s-%s-%s-%04i"
           ) % (ts.year, row['wfo'], row['phenomena'], row['significance'],
                row['eventid'])
    altxt = "Click for text/image"
    imagemap.write(("<area href=\"%s\" alt=\"%s\" title=\"%s\" "
                    "shape=\"rect\" coords=\"%s,%s,%s,%s\">\n"
                    ) % (url, altxt, altxt, mx0, my, mx0+thumbpx, my+thumbpx))
    i += 1

for i in range(pcursor.rowcount):
    my = int(i / cols) * thumbpx + header
    mx0 = (i % cols) * thumbpx
    if mx0 == 0:
        draw.line((0, my + thumbpx + 2, (thumbpx*cols), my + thumbpx + 2),
                  (0, 120, 200))

mosaic.save("test.png")
del mosaic

imagemap.write("</map>")
imagemap.close()

cmd = ("/home/ldm/bin/pqinsert -p "
       "'plot a %s0000 blah sbwsum%s.png png' test.png"
       ) % (sts.strftime("%Y%m%d"), opts[sortOpt]['fnadd'])
subprocess.call(cmd, shell=True)

cmd = ("/home/ldm/bin/pqinsert -p "
       "'plot a %s0000 blah sbwsum-imap%s.txt txt' imap.txt"
       ) % (sts.strftime("%Y%m%d"), opts[sortOpt]['fnadd'])
subprocess.call(cmd, shell=True)

os.remove("test.png")
os.remove("imap.txt")
