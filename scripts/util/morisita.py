#!/mesonet/python-2.4/bin/python

from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']

networkStr = "(network ~* 'ASOS' or network ~* 'AWOS' or network ~* 'RWIS' or network = 'ISUAG' or network in ('KCCI','KELO','KIMT'))"

# Lets get the bounds first
#sql = "select xmax(e), xmin(e), ymax(e), ymin(e) from \
#       (select extent(transform(geom, 26915)) as e from stations \
#        WHERE network IN %s) as foo" % (networks,)
#rs = mesosite.query(sql).dictresult()
#xmax = int(rs[0]['xmax'])
#xmin = int(rs[0]['xmin'])
#ymax = int(rs[0]['ymax'])
#ymin = int(rs[0]['ymin'])
xmax = 816015
xmin = 102527
ymax = 4913904
ymin = 4395508

# We need stations!
stations = {}
sql = "select id, x(transform(geom, 26915)), y(transform(geom, 26915)) \
       from stations WHERE %s and contains('SRID=4326;POLYGON((-97.632 39.651, -97.632 44.319, -89.317 44.319, -89.317 39.651, -97.632 39.651))',geom) " % (networkStr,)
rs = mesosite.query(sql).dictresult()
for i in range(len(rs)):
    stations[ rs[i]['id'] ] = {'x': int(rs[i]['x']), 'y': int(rs[i]['y']) }

for cellsize in range(10000,300000,10000):
    cellcount = 0
    sum = 0
    for x in range(xmin, xmax, cellsize):
        west = x
        east = x +  cellsize
        for y in range(ymin, ymax, cellsize):
            south = y
            north = y + cellsize
            hits = 0
            for id in stations.keys():
                if ( stations[id]['x'] >= west and stations[id]['x'] < east and \
                 stations[id]['y'] >= south and stations[id]['y'] < north ):
                    hits += 1
            sum += hits * (hits -1)
            cellcount += 1

    stns = float(len(stations.keys()))
    ind = float(cellcount) * float(sum) / (stns * (stns-1.0))
    #print "%s,%s,%s" % (cellsize, ind, cellcount)
    print "%s" % (ind)
