"""
Split up the Hourly files from Unidata
"""
import mx.DateTime
import os

sts = mx.DateTime.DateTime(2012,6,19, 19)
ets = mx.DateTime.DateTime(2012,6,20, 1)
interval = mx.DateTime.RelativeDateTime(hours=1)

now = sts
while now < ets:
    out = open('%s.data' % (now.strftime("%Y%m%d%H"),), 'w')

    data = open( now.strftime('SURFACE_DDPLUS_%Y%m%d_%H00.txt'), 'r').read()
    tokens = data.split("\003\001")
    del data
    for product in tokens:
        lines = product.split("\r\r\n")
        #if len(lines[3]) > 5 and lines[3][:3] in ('MWW','FWW','CFW','TCV','RFW',
        #        'FFA','SVR','TOR','SVS','SMW','MWS','NPW','WCN','WSW','EWW',
        #        'FLS','FLW','FFW','FFS','HLS','TSU'):
        if len(lines[3]) == 6:
            out.write("\001%s\003" % (product,))

    out.close()
    now += interval