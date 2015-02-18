import datetime
import urllib2
sts = datetime.datetime(2008,8,26,20,0)
ets = datetime.datetime(2008,8,27,2,0)
interval = datetime.timedelta(minutes=1)

frame = 0
while sts < ets:
    print sts
    data = urllib2.urlopen(sts.strftime("http://iem.local/mec/map_power_%Y%m%d%H%M_yaw3.png"))
    img = data.read()
    for i in range(6):
        o = open("power_movie/%05i.png" % (frame, ), 'wb')
        o.write(img)
        o.close()
        frame += 1
    sts += interval