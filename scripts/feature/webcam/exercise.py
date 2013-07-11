import Image

img = Image.open('veryred.jpg' )

im2 = img.crop((0,0,640,320))
print  im2.resize( (1,1), Image.ANTIALIAS).getpixel((0,0))
im2.save('test.jpg')