# Something to store constants of our effort

# Iowa Extents in EPSG:26915
# 202,054 4,470,570 736,852 4,822,687
# Or! 352km by 535km
# So for ~25km, we'd want 23x and 15y
SOUTH =  40.1356
WEST  = -96.8732
NORTH =  43.7538
EAST  = -89.6463

NX = 24
NY = 16

DX = (EAST-WEST)/float(NX-1)
DY = (NORTH-SOUTH)/float(NY-1)
