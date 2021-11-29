#!/usr/bin/env python3

from PIL import Image, ImageOps
import sys
import mtp02_ioctl

img = Image.open(sys.argv[1])

basewidth = 384

wpercent = (basewidth/float(img.size[0]))
if wpercent < 1:
	hsize = int((float(img.size[1])*float(wpercent)))
	img = img.resize((basewidth,hsize), Image.ANTIALIAS)

ki = img.convert("RGB")
pal_image= Image.new("P", (1,1))
pal_pal = list((0,0,0,127,127,127,255,255,255))
pal_pal.extend((0,0,0)*(256-3))
pal_image.putpalette(pal_pal)
ki = ki.quantize(colors=3,palette=pal_image,method=Image.LIBIMAGEQUANT) # Grayscale

width, height = ki.size
result = Image.new(ki.mode, (384, height), 0)
result.paste(ki, (0, 0))

f=open("/dev/mtp02.0","wb")

settings=mtp02_ioctl.get_settings(f)
settings['line_feed'] = 0
mtp02_ioctl.set_settings(f,settings)

for line in range(result.height):
    grayline = bytes()
    blackline = bytes()
    for pixelgroup in range(0,result.width,8):
        graybyte = 0
        blackbyte = 0
        for i in range(8):
            pixel = result.getpixel((pixelgroup+i,line))
            if pixel == 1:
                graybyte |= 1<<(7-i)
            if pixel == 0:
                blackbyte |= 1<<(7-i)
        grayline+=bytes([graybyte])
        blackline+=bytes([blackbyte])

    settings['burn_time'] = 125
    mtp02_ioctl.set_settings(f,settings)
    f.write(grayline)
    f.flush()
    settings['burn_time'] = 250
    mtp02_ioctl.set_settings(f,settings)
    f.write(blackline)
    f.flush()
    mtp02_ioctl.feed(f,2)
