from PIL import Image
import colorsys
import datetime
import urllib2
import os
import ephem
import psycopg2
import shutil
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = ASOS.cursor()
sun = ephem.Sun()
myloc = ephem.Observer()
myloc.lat = '41.99206'
myloc.long = '-93.62183'

sts = datetime.datetime(2006, 7, 22)
ets = datetime.datetime(2013, 7, 11)

output = open('results.txt', 'w')

now = sts
maxv = 0
sunrises = 0
sunsets = 0
while now < ets:
    myloc.date = now.strftime("%Y/%m/%d")
    sunrise = datetime.datetime.strptime("%s" % (myloc.next_rising(sun),),
                                         '%Y/%m/%d %H:%M:%S')
    sunrise = sunrise.replace(second=0)
    sunrise = sunrise - datetime.timedelta(minutes=sunrise.minute % 10)

    sunset = datetime.datetime.strptime("%s" % (myloc.next_setting(sun),),
                                        '%Y/%m/%d %H:%M:%S')
    sunset = sunset.replace(second=0)
    sunset = sunset - datetime.timedelta(minutes=sunset.minute % 10)

    uri = sunrise.strftime(('https://mesonet.agron.iastate.edu/archive/'
                            'data/%Y/%m/%d/camera/KCCI-026/'
                            'KCCI-026_%Y%m%d%H%M.jpg'))
    try:
        data = urllib2.urlopen(uri).read()
    except urllib2.HTTPError:
        print 'Download failed'
        now += datetime.timedelta(days=1)
        continue
    sunrises += 1
    o = open('webcam.jpg', 'w')
    o.write(data)
    o.close()

    f = Image.open('webcam.jpg')
    (w, h) = f.size
    """
    c = f.getcolors(w*h)

    redish = 0
    for i, (cnt, rgb) in enumerate(c):
        hsv = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
        if hsv[0] > 0:
            if (hsv[0] < 0.06 or hsv[0] > 0.94) and hsv[1] > 0.9 and hsv[2] > 0.9:
                redish += cnt
    """
    (redish, g, b) = f.resize((1, 1), Image.ANTIALIAS).getpixel((0, 0))

    if redish > 120 and g < 110:  # Our arb thresholding
        print 'RISE', sunrise, redish, w * h,
        output.write('RISE,%s,%s,' % (sunrise, redish))
        cursor.execute("""SELECT sum(p01i) from t""" + str(sunrise.year) + """
        WHERE station = 'AMW' and valid BETWEEN '%s+00' and '%s+00'""" % (
                        (sunrise + datetime.timedelta(hours=1)
                         ).strftime("%Y-%m-%d %H:%M"),
                        (sunrise + datetime.timedelta(days=1)
                         ).strftime("%Y-%m-%d %H:%M")))
        row = cursor.fetchone()
        if row[0] >= 0.01:
            print ' ... HIT'
            output.write("1\n")
        else:
            print ' ... MISS'
            output.write("0\n")

    """
    if redish > 120 and g > 110:
        shutil.copyfile('webcam.jpg', '/tmp/examples/%3f_%3f_%3f.jpg' % (redish,g,b))
    """
    diff = (redish - g) + (redish - b)
    if diff > maxv:
        maxv = redish
        os.rename('webcam.jpg', 'max2.jpg')

    uri = sunset.strftime(('https://mesonet.agron.iastate.edu/archive/data/'
                           '%Y/%m/%d/camera/KCCI-016/KCCI-016_%Y%m%d%H%M.jpg'))
    try:
        data = urllib2.urlopen(uri).read()
    except urllib2.HTTPError:
        print 'Download failed'
        now += datetime.timedelta(days=1)
        continue
    sunsets += 1
    o = open('webcam.jpg', 'w')
    o.write(data)
    o.close()

    f = Image.open('webcam.jpg')
    (w, h) = f.size
    (redish, g, b) = f.resize((1, 1), Image.ANTIALIAS).getpixel((0, 0))

    if redish > 120 and g < 110:  # Our arb thresholding
        print 'SET', sunset, redish, w * h,
        output.write('SET,%s,%s,' % (sunset, redish))
        cursor.execute("""SELECT sum(p01i) from t""" + str(sunrise.year) + """
        WHERE station = 'AMW' and valid BETWEEN '%s+00' and '%s+00'""" % (
                        (sunset + datetime.timedelta(hours=1)
                         ).strftime("%Y-%m-%d %H:%M"),
                        (sunset + datetime.timedelta(days=1)
                         ).strftime("%Y-%m-%d %H:%M")))
        row = cursor.fetchone()
        if row[0] >= 0.01:
            print ' ... HIT'
            output.write("1\n")
        else:
            print ' ... MISS'
            output.write("0\n")

    diff = (redish - g) + (redish - b)
    if diff > maxv:
        maxv = redish
        os.rename('webcam.jpg', 'max2.jpg')

    now += datetime.timedelta(days=1)

output.close()
# 2338 2334
print sunrises, sunsets
