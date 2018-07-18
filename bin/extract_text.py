#!/usr/bin/python


import pytesseract
from sys import argv
from PIL import Image
from PIL import ImageFilter


# set pixels by averaging nearby pixels
def smoothing_filter(im, radius, threshold):

  im2 = Image.new("P", im.size, 255)

  for x in range(im.size[1]):
    for y in range(im.size[0]):

      n = 0
      count = 0
      found = False
      for xx in range(max(0, x-radius), min(x+radius, im.size[1])):
        for yy in range(max(0, y-radius), min(y+radius, im.size[0])):
          if im.getpixel((y,x)) == 255:
            found = True
          n = n + im.getpixel((yy,xx))
          count = count + 1

      # Add a little extra white if any white is found
      if found:
        n = n + 255*radius

      val = n/count
      if val > threshold:
        val = 255
      im2.putpixel((y,x), val)

  return im2

# set pixels by averaging nearby pixels
def filling_filter(im, radius, threshold):

  im2 = Image.new("P", im.size, 255)

  for x in range(im.size[1]):
    for y in range(im.size[0]):

      n = 0
      count = 0
      for xx in range(max(0, x-radius), min(x+radius, im.size[1])):
        for yy in range(max(0, y-radius), min(y+radius, im.size[0])):
          n = n + im.getpixel((yy,xx))
          count = count + 1

      val = n/count
      if val <= threshold:
        val = 0
      else:
        val = im.getpixel((y,x))
      im2.putpixel((y,x), val)

  return im2


# find letters within the image
def letter_clip(im):

  top = -1
  left = -1
  right = -1
  bottom = -1

  for x in range(im.size[0]):
    for y in range(im.size[1]):

      if im.getpixel((x, y)) < 220:
        if top == -1 or y < top:
           top = y
        if left == -1 or x < left:
           left = x
        if bottom == -1 or y > bottom:
           bottom = y
        if right == -1 or x > right:
           right = x
 
  top = max(0, top - 5)
  bottom = min(bottom + 5, im.size[1])
  left = max(0, left - 5)
  right = min(right + 5, im.size[0])

  return im.crop((left, top, right, bottom))


# find letters within the image
def letter_iterator(im):

  images = []
  boundary = []
  found = False

  for x in range(im.size[0]):

    n = 0
    for y in range(im.size[1]):
      if im.getpixel((x, y)) > 220:
        n = n + 1

    if n == im.size[1]:
      if not found:
         boundary.append(x)
         found = True
    else:
      found = False

  h = im.size[1]
  for i in range(len(boundary) - 1):
    im2 = im.crop((boundary[i], 0, boundary[i+1], h))
    if boundary[i+1] - boundary[i] < 20:
        continue
    im2 = im2.resize((im2.size[0]*5, im2.size[1]*5))
    images.append(im2)

  return images


# Load the image in greyscale
im = Image.open(argv[1])
im = im.convert("L", (.4,.4,.35,0))
im = im.resize((im.size[0]*2, im.size[1]*2))

# Average and clip out the letters
im = smoothing_filter(im, 2, 240)
im = filling_filter(im, 2, 230)
im = smoothing_filter(im, 2, 220)
#im = smoothing_filter(im, 1, 200)

# Extract the character for each letter using several orientations
text = []
for i in range(4):
    text.append("")

for i in letter_iterator(im):
    # clip and rotate right
    i = letter_clip(i)
    i = i.convert("RGBA")
    i = i.rotate(25, expand=True, center=(i.size[0], i.size[1]))
    i = Image.composite(i, Image.new('RGBA', i.size, (255,)*4), i)
    i = i.convert("L")
    for j in range(len(text)):
      # rotate left and keep track of each decoding
      letter = pytesseract.image_to_string(i, config='-psm 10')
      text[j] = "%s%s" % (text[j], letter.lower())
      i = i.convert("RGBA")
      i = i.rotate(-6, expand=True, center=(i.size[0], i.size[1]))
      i = Image.composite(i, Image.new('RGBA', i.size, (245,)*4), i)
      i = i.convert("L")
  
# Map the frequency of each result
letters = [{}, {}, {}, {}]
for t in range(len(text)):

  for i in range(4):
    if i >= len(text[t]):
      continue

    m = letters[i]
    k = text[t][i]
    v = m.get(k)
    if v == None:
      v = 0
    v = v + 1
    m[k] = v

print(letters)

# Construct a result from the most likely interpretations
result = ""
for m in letters:
  if len(m) == 0:
    continue
  result = "%s%s" % (result, sorted(m, key=m.get, reverse=True)[0])

im.save("output.png")
print(result)
