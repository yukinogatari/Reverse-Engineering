################################################################################
# Copyright © 2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os
from PIL import Image

from util import *

################################################################################
### GLOBALS
################################################################################

PREV_PIXELS = []
PREV_WIDTH  = 0
PREV_HEIGHT = 0

################################################################################

# http://stackoverflow.com/a/5996949
def clamp(n, minn, maxn):
  return max(min(maxn, n), minn)

################################################################################

def save_image(out_file, width, height, pixels):
  
  if not pixels:
    return
  
  # print width, height
  if not len(pixels) == width * height:
    print "Incorrect number of pixels???"
    print len(pixels), width * height
    print
    
    height = len(pixels) / width
    pixels = pixels[:width * height]
  
  # Flatten our pixel array.
  pixels = bytearray([color for pixel in pixels for color in pixel])
  
  img = Image.frombuffer("RGBA", (width, height), pixels, "raw", "RGBA", 0, 1)
  
  img.save(out_file)

################################################################################

def erogos_img_conv(filename, out_file):
  with open(filename, "rb") as f:
    data = bytearray(f.read())
  
  width, height, pixels = erogos_img_parse(data)
  save_image(out_file, width, height, pixels)

################################################################################
  
def erogos_img_parse(data, offset = 0, compose = True):
  global PREV_PIXELS, PREV_WIDTH, PREV_HEIGHT
  
  img_flags = data[offset]
  
  # Adds a 128-entry palette to the header.
  indexed    = not img_flags & 0b00010000
  # Don't pull pixels from the previous image.
  clear_prev =     img_flags & 0b00001000
  # ???
  unk_flag   =     img_flags & 0b00000100
  # Only contains image data for a portion of the full dimensions.
  # Adds an X offset, Y offset, and sub width/height to the header.
  shifted    =     img_flags & 0b00000010
  # Use the previous image exactly as-is.
  copy_prev  =     img_flags & 0b00000001
  
  if copy_prev:
    return PREV_WIDTH, PREV_HEIGHT, PREV_PIXELS
  
  if img_flags >= 0b00100000:
    print "Unknown type: 0x%02X" % img_flags
    return 0, 0, []
  
  if clear_prev:
    PREV_PIXELS = []
  
  xoffset  = 0
  yoffset  = 0
  real_w   = to_u16(data[offset + 1 : offset + 3])
  real_h   = to_u16(data[offset + 3 : offset + 5])
  width    = real_w
  height   = real_h
  
  pos = offset + 5
  
  palette = []
  pixels = []
  
  if shifted:
    xoffset  = to_u16(data[offset + 5 : offset + 7])
    yoffset  = to_u16(data[offset + 7 : offset + 9])
    width    = to_u16(data[offset + 9 : offset + 11])
    height   = to_u16(data[offset + 11 : offset + 13])
    pos      = offset + 13
    
    if yoffset > 0:
      if PREV_PIXELS and compose:
        pixels.extend(PREV_PIXELS[:real_w * yoffset])
      else:
        pixels.extend([[0, 0, 0, 0]] * real_w * yoffset)
  
  if indexed:
    for i in range(128):
      b = data[pos]
      g = data[pos+1]
      r = data[pos+2]
      pos += 3
      palette.append((r, g, b, 0xFF))
  
  while len(pixels) < real_w * height:
    b = data[pos]
    pos += 1
    
    if xoffset and len(pixels) % real_w == 0:
      if PREV_PIXELS and compose:
        pixels.extend(PREV_PIXELS[len(pixels) : len(pixels) + xoffset])
      else:
        pixels.extend([[0, 0, 0, 0]] * xoffset)
    
    # Start of a pixel.
    if b >= 0x80:
      if indexed:
        pixel = palette[b - 0x80]
        # pixel = (b - 0x80,)
        # print "0x80 @ 0x%08X [%3dx%3d]: Palette" % (pos, len(pixels) % real_w, len(pixels) / real_w), "0x%02X" % (b - 0x80), pixel
      
      else:
        # This is stupid/weird, but whatever.
        # If we're 0xC0 or above, the value becomes a bitfield that modifies
        # the value of the previous pixel up or down based on what bits are set.
        if b >= 0xC0:
          
          b_sign = 1 if b & 0b00100000 else -1
          b_mult = 0 if b & 0b00010000 else  2
          g_sign = 1 if b & 0b00001000 else -1
          g_mult = 0 if b & 0b00000100 else  2
          r_sign = 1 if b & 0b00000010 else -1
          r_mult = 0 if b & 0b00000001 else  2
          
          r = clamp(pixels[-1][0] + (r_sign * r_mult), 0, 255)
          g = clamp(pixels[-1][1] + (g_sign * g_mult), 0, 255)
          b = clamp(pixels[-1][2] + (b_sign * b_mult), 0, 255)
          a = pixels[-1][3]
          
          pixel = (r, g, b, a)
          
          # print "0x80 @ 0x%08X [%3dx%3d]: Rel" % (pos, len(pixels) % real_w, len(pixels) / real_w), pixels[-1], "->", pixel
          
        else:
          b = (b - 0x80) * 4
          g = data[pos]
          r = data[pos+1]
          pos += 2
          pixel = (r, g, b, 0xFF)
          # print "0x80 @ 0x%08X [%3dx%3d]: Raw" % (pos, len(pixels) % real_w, len(pixels) / real_w), pixel
      
      pixels.append(pixel)
    
    else:
      flag  = b >> 4
      count = b & 0b1111
      
      if count == 0:
        count = 0x0F
        while data[pos] == 0xFF:
          count += 0xFF
          pos += 1
        count += data[pos]
        pos += 1
      
      # Fully transparent (compose w/ previous frame if available).
      if flag == 0:
        offset = len(pixels)
        # print "0x00 @ 0x%08X [%3dx%3d]: Blank" % (pos, len(pixels) % real_w, len(pixels) / real_w), "x%d" % count
        if PREV_PIXELS and compose:
          pixels.extend(PREV_PIXELS[offset : offset + count])
        else:
          pixels.extend([[0, 0, 0, 0]] * count)
      
      # Copy from this frame.
      else:
      
        # Previous row, right one.
        if flag == 7:
          offset = real_w - 2
          
        # Previous row, right one.
        elif flag == 6:
          offset = real_w - 1
        
        # Previous row.
        elif flag == 5:
          offset = real_w
        
        # Previous row, left one.
        elif flag == 4:
          offset = real_w + 1
        
        # Previous row, left two.
        elif flag == 3:
          offset = real_w + 2
        
        # Previous row, left three.
        elif flag == 2:
          offset = real_w + 3
        
        # Previous pixel.
        elif flag == 1:
          offset = 1
        
        # print "0x02X @ 0x%08X [%3dx%3d]: Copying" % (flag << 4, pos, len(pixels) % real_w, len(pixels) / real_w), count, "pixels from %dx%d" % (offset % real_w, offset / real_w)
        
        for i in range(count):
          pixels.append(pixels[-offset])
    
    if not width == real_w and len(pixels) % real_w == width:
      if PREV_PIXELS and compose:
        pixels.extend(PREV_PIXELS[len(pixels) : len(pixels) + (real_w - width)])
      else:
        pixels.extend([[0, 0, 0, 0]] * (real_w - width))
  
  if not height == real_h:
    if PREV_PIXELS and compose:
      pixels.extend(PREV_PIXELS[real_w * height:])
    else:
      pixels.extend([[0, 0, 0, 0]] * real_w * (real_h - height))
  
  PREV_PIXELS = pixels
  PREV_WIDTH  = real_w
  PREV_HEIGHT = real_h
  
  return real_w, real_h, pixels

################################################################################

def erogos_ani_ex(filename, out_dir, compose = True):
  f = BinaryFile(filename, "rb")
  
  frame_offs = []
  
  while True:
    frame_offs.append(f.get_u32())
    
    if f.tell() >= frame_offs[0]:
      break
    
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  f.seek(0)
  data = bytearray(f.read())
  
  global PREV_PIXELS, PREV_WIDTH, PREV_HEIGHT
  PREV_PIXELS = []
  PREV_WIDTH  = 0
  PREV_HEIGHT = 0
  
  for i, offset in enumerate(frame_offs):
    
    out_file = os.path.join(out_dir, "%04d.png" % i)
    print out_file
    
    width, height, pixels = erogos_img_parse(data, offset, compose)
    
    if not pixels and not data[offset] == 0x01:
      # print i, frame
      out_file = os.path.splitext(out_file)[0] + ".bin"
      with open(out_file, "wb") as f:
        f.write(data[offset:])
      continue
    
    save_image(out_file, width, height, pixels)

################################################################################
  
if __name__ == "__main__":
  
  dirs = [
    "maho1",
    # "maho2",
    # "maho3",
    # "maho4",
    # "maho5",
    # "maho6",
    # "lf1",
    # "lf2",
    # "lf3",
    # "lf4",
    # "lf5",
    # "lf6",
    # "lf7-1",
    # "lf7-2",
    # "lf7-3",
    # "lf7-4",
    # "lf7-5",
    # "lf7-6",
    # "lf8",
    # "lf9",
    # "lf10",
  ]
  
  for dirname in dirs:
    bg_dir = os.path.join(dirname + "-ex", "bg")
    mov_dir = os.path.join(dirname + "-ex", "mov")
    af_dir = os.path.join(dirname + "-ex", "af")
    
    if os.path.isdir(bg_dir):
      for filename in os.listdir(bg_dir):
        base, ext = os.path.splitext(filename)
        if not os.path.splitext(filename)[1].lower() == ".cg":
          continue
        
        print filename
        in_file  = os.path.join(bg_dir, filename)
        out_file = os.path.join(bg_dir, base + ".png")
        erogos_img_conv(in_file, out_file)
      
    if os.path.isdir(mov_dir):
      for filename in os.listdir(mov_dir):
        base, ext = os.path.splitext(filename)
        if not ext.lower() == ".ani":
          continue
        
        print filename
        in_file = os.path.join(mov_dir, filename)
        out_dir = os.path.join(mov_dir, base)
        erogos_ani_ex(in_file, out_dir, compose = True)
      
    if os.path.isdir(af_dir):
      for filename in os.listdir(af_dir):
        base, ext = os.path.splitext(filename)
        if not ext.lower() == ".ani":
          continue
        
        print filename
        in_file = os.path.join(af_dir, filename)
        out_dir = os.path.join(af_dir, base)
        erogos_ani_ex(in_file, out_dir, compose = True)

### EOF ###