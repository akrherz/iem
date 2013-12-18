# Generate a color ramp image, please
import Image, ImageDraw, ImageFont
import numpy
import nmq

font = ImageFont.truetype("/home/akrherz/projects/pyVBCam/lib/veramono.ttf", 10)

def make_gr_colorramp():
    """
    Make me a crude color ramp
    """
    c = numpy.zeros((256,3), numpy.int)
    
    # Gray for missing
    c[0,:] = [144,144,144]
    # Black to remove, eventually
    c[1,:] = [0,0,0]
    i = 2 
    for line in open('gr2ae.txt'):
        c[i,:] = map(int, line.split()[-3:])
        i+=1
    c[255,:] = [255,255,255]
    return tuple( c.ravel() )

data = numpy.zeros( (30,256), numpy.uint8)

for i in range(255):
    data[0:15,i:i+1] = i

png = Image.fromarray( data )
#png.putpalette( make_gr_colorramp() )
png.putpalette( nmq.make_colorramp() )
draw = ImageDraw.Draw(png)

#24h Precip
#         0-1   -> 100 - 0.01 res ||  0 - 25   -> 100 - 0.25 mm  0
#         1-5   -> 80 - 0.05 res  ||  25 - 125 ->  80 - 1.25 mm  100
#         5-20  -> 75 - 0.20 res  || 125 - 500  ->  75 - 5 mm    180
xs = [25, 50, 75, 100, 120, 140, 160, 180, 190, 205, 230]
ys = [0.25, 0.5, 0.75, 1, 2, 3, 4, 5, 7, 10, 15]
# 1hr precip
# 1 mm resolution
xs = numpy.arange(25,255, 25)
ys = numpy.arange(1,10)

for x,y in zip(xs, ys):
    (w,h) = font.getsize(`y`)
    draw.line( [x,17,x,10], fill=255)
    draw.text( (x-(w/2),18), `y`,fill=255, font=font)
draw.text( (235,18), 'in',fill=255, font=font)

""" 
#DBZ
for x in range(6,235,20):
    dbz = int(x/2.0 - 33)
    (w,h) = font.getsize(`dbz`)
    draw.line( [x,17,x,10], fill=255)
    draw.text( (x-(w/2),18), `dbz`,fill=255, font=font)
draw.text( (235,18), 'dBZ',fill=255, font=font)
"""

#draw.line( [0,0,255,0,255,29,0,29,0,0], fill=255)

png.save("test.png")

