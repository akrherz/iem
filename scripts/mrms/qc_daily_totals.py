"""
Check on our rasters, please
"""
import mx.DateTime
import osgeo.gdal as gdal
import numpy
import nmq
sts = mx.DateTime.DateTime(2012,5,2,5)
ets = mx.DateTime.DateTime(2012,6,23,5)
interval = mx.DateTime.RelativeDateTime(days=1)

ul_x, ul_y = nmq.get_image_xy(-93.66308, 41.53397)

total = 0
now = sts
while now < ets:
    fp = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/q2/p24h_%Y%m%d%H00.png")
    img = gdal.Open(fp, 0)
    data = img.ReadAsArray()
    precip = numpy.zeros( numpy.shape(data), 'f')
    precip = numpy.where( numpy.logical_and(data < 255, data >= 180),
                              125.0 + ((data - 180) * 5.0), precip )
    precip = numpy.where( numpy.logical_and(data < 180, data >= 100),
                              25.0 + ((data - 100) * 1.25), precip )
    precip = numpy.where( data < 100,
                              0.0 + ((data - 0) * 0.25), precip )
    del img
    print now, data[ul_y,ul_x], (precip[ul_y,ul_x]  ) / 25.4
    total += (precip[ul_y,ul_x] )  / 25.4
    now += interval

print total