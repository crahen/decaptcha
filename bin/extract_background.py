#!/usr/bin/python

import os
from PIL import Image


image = []
mask = None


# Load each image in grey scale
for f in os.listdir("data"):
  if not f.endswith(".jpg"):
    continue

  i = Image.open("data/%s" % (f))
  #i = i.convert("L")
  image.append(i)


# Create a mask clearing pixels that appear in all images
for n in range(len(image)):

  if mask == None:
    mask = Image.new("RGB", image[n].size, (255, 255, 255))
    #mask = Image.new("L", image[n].size, 255)

  for x in range(image[n].size[1]):
    for y in range(image[n].size[0]):

      val = image[n].getpixel((y,x))
      r = val[0]
      g = val[1]
      b = val[2]
      for m in range(len(image)):

        val = image[m].getpixel((y,x))
        r = (val[0] + r) / 2
        g = (val[1] + g) / 2
        b = (val[2] + b) / 2

      if (r > 0xd0 and b < 0xdd and g < 0xdd) or (r > 0xd0 and g < 0xdd and b < 0xdd):
         mask.putpixel((y,x), (r,g,b))

      if (b > 0xd0 and r < 0xdd and g < 0xdd) or (b > 0xd0 and g < 0xdd and r < 0xdd):
         mask.putpixel((y,x), (r,g,b))

      if (g > 0xd0 and r < 0xdd and b < 0xdd) or (g > 0xd0 and b < 0xdd and r < 0xdd):
         mask.putpixel((y,x), (r,g,b))

mask.save("mask.png", dpi=(200,200))

n = 5
for x in range(image[n].size[1]):
  for y in range(image[n].size[0]):

    if mask.getpixel((y,x)) == (255, 255, 255):
      continue

    val = image[n].getpixel((y,x))
    #val = max(val, mask.getpixel((y,x))/2) - min(val, mask.getpixel((y,x))/2)
    #image[n].putpixel((y,x), val)

    r = val[0]
    g = val[1]
    b = val[2]
    r = max(r, mask.getpixel((y,x))[0]) - min(r, mask.getpixel((y,x))[0]) 
    g = max(g, mask.getpixel((y,x))[1]) - min(g, mask.getpixel((y,x))[1]) 
    b = max(b, mask.getpixel((y,x))[2]) - min(b, mask.getpixel((y,x))[2]) 
    image[n].putpixel((y,x), 0)

    #r = r - mask.getpixel((y,x))[0]
    #g = g - mask.getpixel((y,x))[1]
    #b = b - mask.getpixel((y,x))[2]
    #image[n].putpixel((y,x), (abs(r), abs(g), abs(b)))

image[n].save("output.png", dpi=(200,200))
