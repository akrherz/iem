
import gd

xwidth = 800
yheight = 500

im = gd.image((xwidth,yheight))

# Allocate Colors          
red = im.colorAllocate((255,0,0))
green = im.colorAllocate((0,255,0))
blue = im.colorAllocate((0,0,255))
black = im.colorAllocate((0,0,0))
white = im.colorAllocate((255,255,255))
lgreen = im.colorAllocate((127,125,85))

label = gd.gdFontMediumBold
title = gd.gdFontGiant

