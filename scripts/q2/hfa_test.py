from osgeo import gdal as gdal
from osgeo import osr as osr

sr = osr.SpatialReference()
sr.ImportFromEPSG(4326)

drv = gdal.GetDriverByName('HFA')
ds = drv.Create('test.img', 7000, 5000, 1, gdal.GDT_Float32, [])
ds.SetProjection(sr.ExportToWkt())

# top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
ds.SetGeoTransform( [ -95.0, 0.01, 0, 50.0, 0, -0.01 ] )


ds = None