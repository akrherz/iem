# Combine DM layers into one shapefile!
# Daryl Herzmann 4 Nov 2005

import mapscript, dbflib, sys, os
ts = sys.argv[1]

outshp = mapscript.shapefileObj('dm_%s.shp'%ts, mapscript.MS_SHAPEFILE_POLYGON )

dbf = dbflib.create("dm_%s"%ts)
dbf.add_field("DCAT", dbflib.FTInteger, 1, 0)

counter = 0
for d in range(5):
  if not os.path.isfile("Drought_Areas_US_D%s.shp" %d):
    print "No Shapefile for D %s" % (d,)
    continue
  shp = mapscript.shapefileObj('Drought_Areas_US_D%s.shp' %d)

  for i in range( shp.numshapes ):
    shpObj = shp.getShape(i)
    outshp.add( shpObj )
    dbf.write_record(counter, [d,])
    del shpObj
    counter += 1

del outshp
del dbf
