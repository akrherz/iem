#!/mesonet/python/bin/python
# Generate a calendar of temperatures! :)

from PIL import Image, ImageDraw, ImageFont
import mx.DateTime, pg
from pyIEM import iemdb
i = iemdb.iemdb()

climatedb = i['coop']
iemdb = i['iem']

font = ImageFont.truetype('/mesonet/data/gis/static/fonts/Vera.ttf', 22)
font12 = ImageFont.truetype('/mesonet/data/gis/static/fonts/Vera.ttf', 12)
font6 = ImageFont.truetype('/mesonet/data/gis/static/fonts/Vera.ttf', 10)

boxsize = 40
header = 40
linesize = 2

out = Image.new('RGB', (boxsize*7 + linesize, boxsize*6 + linesize + header), color="#fff")
draw = ImageDraw.Draw(out)

draw.text( (10, 5), "Feb 2011 Ames Daily High Temp Difference" , font=font12, fill="#000")

s = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
for k in range(len(s)):
  draw.text( (k * boxsize + 8 , 25), s[k], font=font12, fill="#000")

sts = mx.DateTime.DateTime(2011,2,1)
ets = mx.DateTime.DateTime(2011,2,28)
interval = mx.DateTime.RelativeDateTime(days=+1)
now = sts
(isoyear, startweek, isoday) = now.iso_week

# Load up obs
obs = {}
#sql = "SELECT extract(day from day) as d, (max_tmpf + min_tmpf) / 2 as t \
sql = "SELECT extract(day from day) as d, max_tmpf as t \
       from summary_2011 WHERE day >= '%s' and day < '%s' and station = 'AMW' " \
       % (sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d") )
rs = iemdb.query(sql).dictresult()
for i in range(len(rs)):
  obs[ int(rs[i]['d']) ] = float( rs[i]['t'] )

# Load up climate
climate = {}
#sql = "SELECT extract(day from valid) as d, (high + low) / 2 as t \
sql = "SELECT extract(day from valid) as d, high as t \
       from climate51 WHERE valid >= '2000-%s' and valid < '2000-%s' and \
       station = 'ia0200'" % (sts.strftime("%m-%d"), ets.strftime("%m-%d") )
rs = climatedb.query(sql).dictresult()
for i in range(len(rs)):
  climate[ int(rs[i]['d']) ] = float( rs[i]['t'] )

# Ba
dayxref = [0,1,2,3,4,5,6,0]
weekxref = [0,0,0,0,0,0,0,1]
startweek += weekxref[isoday]

while (now < ets):
    (isoyear, isoweek, isoday) = now.iso_week
    isoweek = isoweek - (sts.iso_week)[1]
    if isoweek < 0: 
       isoweek = 53 + isoweek

    #if (now.day == 1): isoweek = 0
    x = boxsize * (dayxref[isoday])
    y = boxsize * (isoweek + weekxref[isoday] ) + header
    print now, x, y, isoweek
    p = "??"
    c = "#fff"
    if now.day < 32:
      diff = obs[now.day] - climate[ now.day ]
      p = "%i" % (diff,)
      if (diff < 0):
        c = "#00f"
      if (diff > 0):
        c = "#f00"
    draw.rectangle( [(x,y),(x+boxsize,y+boxsize)], fill=c)
    draw.text( (x+7, y+12), p, fill="#000", font=font)
    draw.text( (x+2, y+2), `now.day`, fill="#fff", font=font6)
    now += interval

# Draw 7 vertical bar
for i in range(8):
  xpos = i * boxsize
  draw.rectangle( [(xpos,header),(xpos+linesize,boxsize*5 +linesize + header)], fill="#000")

# Draw 5 horizontal bar
for j in range(6):
  ypos = j * boxsize + header
  draw.rectangle( [(0,ypos),(boxsize*7 +linesize,ypos+linesize)], fill="#000")

out.save('test.png')
del out
