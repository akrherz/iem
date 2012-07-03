
from PIL import Image, ImageDraw, ImageFont
import mx.DateTime
import pg
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

font = ImageFont.truetype('/usr/lib/python2.6/site-packages/PyNGL/ncarg/database/ftfonts/Vera.ttf', 22)
font12 = ImageFont.truetype('/usr/lib/python2.6/site-packages/PyNGL/ncarg/database/ftfonts/Vera.ttf', 12)
font6 = ImageFont.truetype('/usr/lib/python2.6/site-packages/PyNGL/ncarg/database/ftfonts/Vera.ttf', 10)

boxsize = 40
header = 40
linesize = 1

out = Image.new('RGB', (boxsize*7 + linesize, boxsize*7 + linesize + header), color="#fff")
draw = ImageDraw.Draw(out)

draw.text( (10, 5), "1 May - 13 Jun 2012 Daily Iowa Precipitation" , font=font12, fill="#000")

s = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
for k in range(len(s)):
  draw.text( (k * boxsize + 8 , 25), s[k], font=font12, fill="#000")

sts = mx.DateTime.DateTime(2012,5,1)
ets = mx.DateTime.DateTime(2012,6,14)
interval = mx.DateTime.RelativeDateTime(days=+1)
now = sts
(isoyear, startweek, isoday) = now.iso_week

# Load up obs
obs = {}
ccursor.execute("""
 SELECT day, precip from alldata_ia where station = 'IA0000' and year = 2012
 and month in (5,6)
""")
for row in ccursor:
    obs[ row[0].strftime("%Y%m%d") ] = float( row[1] )


# Ba
dayxref = [0,1,2,3,4,5,6,0]
weekxref = [0,0,0,0,0,0,0,1]
startweek += weekxref[isoday]

while now < ets:
    (isoyear, isoweek, isoday) = now.iso_week
    isoweek = isoweek - (sts.iso_week)[1]
    if isoweek < 0: 
       isoweek = 53 + isoweek

    #if (now.day == 1): isoweek = 0
    x = boxsize * (dayxref[isoday])
    y = boxsize * (isoweek + weekxref[isoday] ) + header
    print now, x, y, isoweek
    c = "#fff"
    val = obs.get(now.strftime("%Y%m%d"),0)
    if val > 0.01:
        p = "%.2f" % (val,)
        c = "#00f"
    elif val == 0.01:
        p = "T"
        c = "#000"
    else:
        p = "0"
        c = "#000"
    draw.rectangle( [(x,y),(x+boxsize,y+boxsize)], fill="#fff")
    draw.text( (x+7, y+12), p, fill=c, font=font12)
    draw.text( (x+2, y+2), `now.day`, fill="#000", font=font6)
    now += interval

# Draw 7 vertical bar
for i in range(8):
  xpos = i * boxsize
  draw.rectangle( [(xpos,header),(xpos+linesize,boxsize*7 +linesize + header)], 
                  fill="#000")

# Draw 5 horizontal bar
for j in range(8):
  ypos = j * boxsize + header
  draw.rectangle( [(0,ypos),(boxsize*7 +linesize,ypos+linesize)], fill="#000")

out.save('test.png')
del out
